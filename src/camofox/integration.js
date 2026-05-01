import puppeteer from 'puppeteer';
import { logger } from '../utils/logger.js';

export class CamofoxBrowser {
  constructor(config = {}) {
    this.config = {
      headless: config.headless !== false,
      executablePath: config.executablePath || '/usr/bin/camoufox',
      antiDetection: config.antiDetection !== false,
      proxy: config.proxy || null,
      userAgent: config.userAgent || null,
      ...config
    };

    this.browser = null;
    this.pages = new Map();
  }

  async launch() {
    try {
      const launchArgs = [
        '--no-first-run',
        '--no-default-browser-check'
      ];

      if (this.config.proxy) {
        launchArgs.push(`--proxy-server=${this.config.proxy}`);
      }

      if (this.config.antiDetection) {
        // Anti-detection features
        launchArgs.push('--disable-blink-features=AutomationControlled');
      }

      this.browser = await puppeteer.launch({
        headless: this.config.headless,
        executablePath: this.config.executablePath,
        args: launchArgs
      });

      logger.info('Camoufox browser launched');
      return true;
    } catch (err) {
      logger.error('Failed to launch Camoufox:', err);
      return false;
    }
  }

  async createPage(name = null) {
    try {
      if (!this.browser) {
        throw new Error('Browser not launched. Call launch() first.');
      }

      const page = await this.browser.newPage();
      const pageId = name || `page_${Date.now()}`;

      // Anti-detection measures
      if (this.config.antiDetection) {
        await page.evaluateOnNewDocument(() => {
          Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
          });
        });

        // Spoof user agent if configured
        if (this.config.userAgent) {
          await page.setUserAgent(this.config.userAgent);
        }

        // Set viewport to random size
        await page.setViewport({
          width: 1920 + Math.floor(Math.random() * 100),
          height: 1080 + Math.floor(Math.random() * 100)
        });
      }

      this.pages.set(pageId, page);
      logger.info(`Page created: ${pageId}`);

      return { pageId, page };
    } catch (err) {
      logger.error('Failed to create page:', err);
      return null;
    }
  }

  async goto(pageId, url, options = {}) {
    try {
      const page = this.pages.get(pageId);
      if (!page) {
        throw new Error(`Page not found: ${pageId}`);
      }

      await page.goto(url, { waitUntil: 'networkidle2', ...options });
      logger.info(`Navigated to ${url} on ${pageId}`);
      return true;
    } catch (err) {
      logger.error(`Navigation failed for ${pageId}:`, err);
      return false;
    }
  }

  async scrapeData(pageId, selector) {
    try {
      const page = this.pages.get(pageId);
      if (!page) {
        throw new Error(`Page not found: ${pageId}`);
      }

      const data = await page.evaluate((sel) => {
        const elements = document.querySelectorAll(sel);
        return Array.from(elements).map(el => ({
          text: el.innerText,
          html: el.innerHTML,
          tagName: el.tagName
        }));
      }, selector);

      return data;
    } catch (err) {
      logger.error(`Data scraping failed for ${pageId}:`, err);
      return null;
    }
  }

  async clickElement(pageId, selector) {
    try {
      const page = this.pages.get(pageId);
      if (!page) {
        throw new Error(`Page not found: ${pageId}`);
      }

      await page.click(selector);
      logger.info(`Clicked element ${selector} on ${pageId}`);
      return true;
    } catch (err) {
      logger.error(`Click failed on ${pageId}:`, err);
      return false;
    }
  }

  async typeText(pageId, selector, text, options = {}) {
    try {
      const page = this.pages.get(pageId);
      if (!page) {
        throw new Error(`Page not found: ${pageId}`);
      }

      await page.click(selector);
      await page.type(selector, text, { delay: 100, ...options });
      logger.info(`Typed text on ${selector} in ${pageId}`);
      return true;
    } catch (err) {
      logger.error(`Type failed on ${pageId}:`, err);
      return false;
    }
  }

  async waitForElement(pageId, selector, timeout = 5000) {
    try {
      const page = this.pages.get(pageId);
      if (!page) {
        throw new Error(`Page not found: ${pageId}`);
      }

      await page.waitForSelector(selector, { timeout });
      return true;
    } catch (err) {
      logger.error(`Wait for element failed on ${pageId}:`, err);
      return false;
    }
  }

  async getPageContent(pageId) {
    try {
      const page = this.pages.get(pageId);
      if (!page) {
        throw new Error(`Page not found: ${pageId}`);
      }

      const content = await page.content();
      return content;
    } catch (err) {
      logger.error(`Get content failed for ${pageId}:`, err);
      return null;
    }
  }

  async closePage(pageId) {
    try {
      const page = this.pages.get(pageId);
      if (page) {
        await page.close();
        this.pages.delete(pageId);
        logger.info(`Page closed: ${pageId}`);
      }
    } catch (err) {
      logger.error(`Close page failed for ${pageId}:`, err);
    }
  }

  async close() {
    try {
      // Close all pages
      for (const [pageId, page] of this.pages) {
        await page.close();
      }
      this.pages.clear();

      // Close browser
      if (this.browser) {
        await this.browser.close();
        logger.info('Camoufox browser closed');
      }
    } catch (err) {
      logger.error('Failed to close browser:', err);
    }
  }

  getPageCount() {
    return this.pages.size;
  }

  getPageIds() {
    return Array.from(this.pages.keys());
  }
}

export default CamofoxBrowser;
