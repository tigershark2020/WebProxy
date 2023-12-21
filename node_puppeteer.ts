const express = require('express')
const replace = require('absolutify')
const puppeteer = require('puppeteer-extra');
// const puppeteer = require('puppeteer-extra-plugin-recaptcha');
// const puppeteer = require('puppeteer');
var sleep = require('sleep'); 

const port = 1337;

const app = express()

app.get('/', async (req, res) => {

    const url = req.query.url
    const time_delay = req.query.time_delay

    if (url == null || url == '') {
        var urlNotSetStatus = "URL Not Set";
        return res.send(urlNotSetStatus);
    } else {
        try {
		const buff = Buffer.from(url, "base64");
		const urlBase64Decoded = buff.toString("utf8");
		console.log(urlBase64Decoded);
		const StealthPlugin = require('puppeteer-extra-plugin-stealth')
		puppeteer.use(StealthPlugin());

		puppeteer.launch({headless: false, ignoreHTTPSErrors: true, args: [`--window-size=1920,1849`,"--ignore-certificate-errors"], executablePath: '/usr/bin/google-chrome', ignoreHTTPSErrors: true, defaultViewport: {width: 1920, height: 1849}}).then(async browser => {
		
			try
			{			
				const page = await browser.newPage();


				await page.setUserAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36");
				
				const response = await page.goto(urlBase64Decoded, {waitUntil: 'load'});
				const headers = response.headers();
				
				let content_type = "";
				
				if("content-type" in headers)
				{
					content_type = headers["content-type"];
				}

				// await page.solveRecaptchas();
				// await autoScroll(page);		
									
				await page.on('requestfailed', request => {
					if(request.failure() != null)
					{
						if(request.failure().errorText != null)
						{
							console.log(`url: ${request.url()}, errText: ${request.failure().errorText}, method: ${request.method()}`);
						}
					}
				});
				
				await page.on('unhandledRejection', (reason, p) => {
				  	console.log('Unhandled Rejection at: Promise', p, 'reason:', reason);
				});
				
				const cookies = await page.cookies()

				await sleep.sleep(parseInt(time_delay))

				// let base64Encoded = Buffer.from(document).toString("base64");


				const imageBuffer = await page.screenshot({
							type: 'png'
			    	});
			    	
				let screenshotBase64String = Buffer.from(imageBuffer).toString("base64");
				let document = await page.evaluate(() => document.documentElement.outerHTML);
				document = replace(document, urlBase64Decoded);
				
				// console.log("Response Status:\t" + response.status());
				let jsonObject = { "HTML" : document, "Screenshot_PNG" :  screenshotBase64String, "Content_Type" : content_type, "Status_Code" : response.status()}
				let responseJSON = JSON.stringify(jsonObject);
				// console.log(responseJSON);
				let base64Encoded = Buffer.from(responseJSON).toString("base64");
				
				console.log("Returning response to client");	
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

app.listen(port, '192.168.1.161', function () {
    console.log('Listening to port:  ' + port);
});
