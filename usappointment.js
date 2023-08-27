const puppeteer = require('puppeteer');
const parseArgs = require('minimist');
const fs = require('fs');
process.chdir(__dirname);
require('dotenv').config();

(async () => {
    const usernameInput = process.env.USVISA_USER;
    const passwordInput = process.env.USVISA_PASSWORD;
    const region = "ca";
    const cookie = process.env.USVISA_COOKIE_PATH;

    //#region Helper functions
    async function waitForSelectors(selectors, frame, options) {
        for (const selector of selectors) {
            try {
                return await waitForSelector(selector, frame, options);
            } catch (err) {
            }
        }
        throw new Error('Could not find element for selectors: ' + JSON.stringify(selectors));
    }

    async function scrollIntoViewIfNeeded(element, timeout) {
        await waitForConnected(element, timeout);
        const isInViewport = await element.isIntersectingViewport({ threshold: 0 });
        if (isInViewport) {
            return;
        }
        await element.evaluate(element => {
            element.scrollIntoView({
                block: 'center',
                inline: 'center',
                behavior: 'auto',
            });
        });
        await waitForInViewport(element, timeout);
    }

    async function waitForConnected(element, timeout) {
        await waitForFunction(async () => {
            return await element.getProperty('isConnected');
        }, timeout);
    }

    async function waitForInViewport(element, timeout) {
        await waitForFunction(async () => {
            return await element.isIntersectingViewport({ threshold: 0 });
        }, timeout);
    }

    async function waitForSelector(selector, frame, options) {
        if (!Array.isArray(selector)) {
            selector = [selector];
        }
        if (!selector.length) {
            throw new Error('Empty selector provided to waitForSelector');
        }
        let element = null;
        for (let i = 0; i < selector.length; i++) {
            const part = selector[i];
            if (element) {
                element = await element.waitForSelector(part, options);
            } else {
                element = await frame.waitForSelector(part, options);
            }
            if (!element) {
                throw new Error('Could not find element: ' + selector.join('>>'));
            }
            if (i < selector.length - 1) {
                element = (await element.evaluateHandle(el => el.shadowRoot ? el.shadowRoot : el)).asElement();
            }
        }
        if (!element) {
            throw new Error('Could not find element: ' + selector.join('|'));
        }
        return element;
    }

    async function waitForFunction(fn, timeout) {
        let isActive = true;
        setTimeout(() => {
            isActive = false;
        }, timeout);
        while (isActive) {
            const result = await fn();
            if (result) {
                return;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        throw new Error('Timed out');
    }

    async function runLogic() {
        //#region Init puppeteer
        const browser = await puppeteer.launch();
        // Comment above line and uncomment following line to see puppeteer in action
        // const browser = await puppeteer.launch({ headless: false });
        const page = await browser.newPage();
        const timeout = 5000;
        const navigationTimeout = 60000;
        page.setDefaultTimeout(timeout);
        page.setDefaultNavigationTimeout(navigationTimeout);
        //#endregion

        //#region Logic

        // Set the viewport to avoid elements changing places 
        {
            const targetPage = page;
            await targetPage.setViewport({ "width": 2078, "height": 1479 })
        }

        // Go to login page
        {
            const targetPage = page;
            await targetPage.goto('https://ais.usvisa-info.com/en-' + region + '/niv/users/sign_in', { waitUntil: 'domcontentloaded' });
        }

        // Click on username input
        {
            const targetPage = page;
            const element = await waitForSelectors([["aria/Email *"], ["#user_email"]], targetPage, { timeout, visible: true });
            await scrollIntoViewIfNeeded(element, timeout);
            await element.click({ offset: { x: 118, y: 21.453125 } });
        }
        console.log("Logging in...");

        // Type username
        {
            const targetPage = page;
            const element = await waitForSelectors([["aria/Email *"], ["#user_email"]], targetPage, { timeout, visible: true });
            await scrollIntoViewIfNeeded(element, timeout);
            const type = await element.evaluate(el => el.type);
            if (["textarea", "select-one", "text", "url", "tel", "search", "password", "number", "email"].includes(type)) {
                await element.type(usernameInput);
            } else {
                await element.focus();
                await element.evaluate((el, value) => {
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }, usernameInput);
            }
        }

        // Hit tab to go to the password input
        {
            const targetPage = page;
            await targetPage.keyboard.down("Tab");
        }
        {
            const targetPage = page;
            await targetPage.keyboard.up("Tab");
        }

        // Type password
        {
            const targetPage = page;
            const element = await waitForSelectors([["aria/Password"], ["#user_password"]], targetPage, { timeout, visible: true });
            await scrollIntoViewIfNeeded(element, timeout);
            const type = await element.evaluate(el => el.type);
            if (["textarea", "select-one", "text", "url", "tel", "search", "password", "number", "email"].includes(type)) {
                await element.type(passwordInput);
            } else {
                await element.focus();
                await element.evaluate((el, value) => {
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }, passwordInput);
            }
        }

        // Tick the checkbox for agreement
        {
            const targetPage = page;
            const element = await waitForSelectors([["#sign_in_form > div.radio-checkbox-group.margin-top-30 > label > div"]], targetPage, { timeout, visible: true });
            await scrollIntoViewIfNeeded(element, timeout);
            await element.click({ offset: { x: 9, y: 16.34375 } });
        }

        // Click login button
        {
            const targetPage = page;
            const element = await waitForSelectors([["aria/Sign In[role=\"button\"]"], ["#new_user > p:nth-child(9) > input"]], targetPage, { timeout, visible: true });
            await scrollIntoViewIfNeeded(element, timeout);
            await element.click({ offset: { x: 34, y: 11.34375 } });
            await targetPage.waitForNavigation();
        }
        console.log("Logged in, updating cookies...");
        let cookies = await page.cookies();
        let cookiesDict = Object.fromEntries(cookies.map(c => [c.name, c.value]));
        await fs.writeFile(cookie, cookiesDict["_yatri_session"], (e) => {
            if (e) {
                console.log(e);
            } else {
                console.log("Updated cookie");
            }
        });
        await browser.close();
    }

    await runLogic();
})();
