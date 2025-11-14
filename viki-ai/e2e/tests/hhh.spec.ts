import { test, expect } from '@playwright/test';
import { Credentials, URLS } from './constants';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '..', '.env') });



test.describe.configure({ mode: 'serial' });

const login = async ({page}) => {
  await page.goto(URLS.qa.HHH);
  page.on('dialog', async dialog => {
    await dialog.accept()
    // await dialog.dismiss();
  })
  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Kinnser/);

  await page.locator("#username").fill(Credentials.qa.username)
  await page.locator("#password").fill(Credentials.qa.password)
  await page.locator("#login_btn").click();
  await page.waitForURL(/.*AM\/Message\/inbox.cfm.*/ig)
  await expect(page).toHaveTitle(/K-Mail/)
}

let lastUrl = ""
test('Can login to Kinnser', async ({ page }) => {
  await login({page})
  // await page.context().storageState({ path: authFile });
  // await page.waitForLoadState()
  await expect(page).toHaveTitle(/K-Mail/)
  lastUrl = page.url();
  // await page.getByRole('link', { name: 'Go To' }).click();
});

test("Can Navigate to Patient's Medication Profile", async ({page, context}) => {
  await login({page})
  await page.getByRole('link', { name: 'Go To' }).click();
  await page.getByRole('link', { name: 'Patient Manager' }).click();
  await page.waitForURL(/.*am\/Patient\/patientbyletter.cfm.*/ig)
  await expect(page).toHaveTitle(/Patient Manager/)

  await page.locator("#A").click()
  await page.locator("#ShowC").click()
  page.waitForTimeout(1000)

  await page.getByRole("link", {name: "a1, HBill198", exact: true}).click();
  await page.waitForURL(/.*am\/Patient\/EditEpisode.cfm.*/ig)

  await page.getByRole("link", {name: "View", exact: true}).click();
  await page.getByRole("link", {name: "Medication Profile"}).click();
  await page.waitForURL(/.*am\/Medication\/MedicationProfile*/ig)
  // medwidget.shadowRoot.querySelectorAll('div.chakra-portal svg')
  // const medwidget
  // const svg = await page.evaluate(() => {
  //   return (window as any).medwidget.shadowRoot.querySelector('div.chakra-portal  svg')
  // })

  await page.locator("#medwidget div.chakra-portal svg").click()
  await page.waitForResponse(resp => resp.url().includes('/v2/medications/import') && resp.status() === 200);
  await page.waitForResponse(resp => resp.url().includes('/v2/attachments/import') && resp.status() === 200);

  page.waitForTimeout(2000)

  await expect(page.getByRole('heading', { name: 'Select documents' })).toBeVisible();
  const documentRow = page.locator('#medwidget [data-cy="table-cell-0-0"]');
  await documentRow.waitFor()

  await page.locator('#medwidget tr[data-cy="table-row-0"]').click();
  await page.getByRole('button', {name: 'Review all 1 document'}).click();
  page.waitForTimeout(2000)

  await page.getByRole('button', {name: 'Add Medication'}).click();

  await page.locator('#medwidget div[label="Search"] input').fill("aspirin 80")
  await page.waitForResponse(resp => resp.url().includes('api/medispan/search') && resp.status() !== 0);

  const firstResultRow = page.locator('#medwidget .medication-autocomplete-table tbody tr:nth-child(1)')
  await firstResultRow.waitFor()
  firstResultRow.click()
  await page.locator('#medwidget div[label="Amount/Dose"] input').fill("1")
  await page.locator('#medwidget div[label="Instructions"] input').fill("Daily 1 Tablet")
  await page.locator('#medwidget input[placeholder="Start Date"]').fill("2024-08-04")
  await page.getByRole('button', {name: 'Create'}).click();

  const firstMedicationRow = page.locator('#medwidget tr[data-cy="table-row-0"]')
  await firstMedicationRow.waitFor()




  // await (svg).click()
  // await page.click(svg)

  // /html/body/div[1]/div[2]/div[1]//div/div[2]/div[1]/div/svg
  // div.chakra-portal > div:nth-child(2) > div:nth-child(1) > div > svg
})

// test('get started link', async ({ page }) => {
//   await page.goto('https://playwright.dev/');

//   // Click the get started link.
//   await page.getByRole('link', { name: 'Get started' }).click();

//   // Expects page to have a heading with the name of Installation.
//   await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
// });
