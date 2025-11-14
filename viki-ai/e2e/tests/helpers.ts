
// export const doLogin = async ({page}) => {
//   await page.goto(URLS.qa.HHH);
//   page.on('dialog', async dialog => {
//     await dialog.accept()
//     // await dialog.dismiss();
//   })
//   // Expect a title "to contain" a substring.
//   await expect(page).toHaveTitle(/Kinnser/);

//   await page.locator("#username").fill(Credentials.qa.username)
//   await page.locator("#password").fill(Credentials.qa.password)
//   await page.locator("#login_btn").click();
//   await page.waitForURL(/.*AM\/Message\/inbox.cfm.*/)
// }
