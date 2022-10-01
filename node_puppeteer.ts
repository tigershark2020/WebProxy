const express = require('express')
const replace = require('absolutify')
// const puppeteer = require('puppeteer-extra');
const puppeteer = require('puppeteer');
const port = 1337;

const app = express()

app.get('/', async (req, res) => {

    const { url } = req.query
    
    if (!url) {
        var urlNotSetStatus = "URL Not Set";
        return res.send(urlNotSetStatus);
    } else {
        try {
		const buff = Buffer.from(url, "base64");
		const urlBase64Decoded = buff.toString("utf8");
		console.log(urlBase64Decoded);
		// const StealthPlugin = require('puppeteer-extra-plugin-stealth')
		// puppeteer.use(StealthPlugin());


		puppeteer.launch({headless: false, ignoreHTTPSErrors: true, executablePath: '/usr/bin/google-chrome', ignoreHTTPSErrors: true, defaultViewport: null, args: ["--ignore-certificate-errors"]}).then(async browser => {
		
			try
			{			
				const page = await browser.newPage();
				
				await page.setUserAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36");
				
				await page.goto(urlBase64Decoded, {waitUntil: 'load'});

				// await autoScroll(page);		
									
				let document = await page.evaluate(() => document.documentElement.outerHTML);

				document = replace(document, urlBase64Decoded);

				let base64Encoded = Buffer.from(document).toString("base64");
				console.log("Returning response to client");
				
									
				page.on('requestfailed', request => {
					console.log(`url: ${request.url()}, errText: ${request.failure().errorText}, method: ${request.method()}`);

				});
				
				page.on('unhandledRejection', (reason, p) => {
				  	console.log('Unhandled Rejection at: Promise', p, 'reason:', reason);
				});
						
						
				return res.send(base64Encoded);
			
			} catch (err) {
				console.log(err);
				let errorString = "e!";
				return res.send(errorString);
			}
			finally
			{
				await browser.close();

			}
			
		});
        } catch (err) {
		console.log(err);

        }
    }
})

async function autoScroll(page){
    await page.evaluate(async () => {
        await new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if(totalHeight >= scrollHeight - window.innerHeight){
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}

app.listen(port, '192.168.1.43', function () {
    console.log('Listening to port:  ' + port);
});
