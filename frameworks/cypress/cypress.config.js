const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || "http://127.0.0.1:8199",
    specPattern: "cypress/e2e/**/*.cy.js",
    supportFile: "cypress/support/e2e.js",
    video: true,
    screenshotOnRunFailure: true,
    retries: { runMode: 2, openMode: 0 },
    viewportWidth: 1280,
    viewportHeight: 720,
    setupNodeEvents(on, config) {
      return config;
    },
  },
  component: {
    specPattern: "cypress/component/**/*.cy.{js,jsx}",
    supportFile: "cypress/support/component.js",
    devServer: {
      framework: "react",
      bundler: "vite",
    },
  },
});
