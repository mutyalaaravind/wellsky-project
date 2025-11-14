interface AppConfig {
  ADMIN_API: string;
}

class ConfigService {
  private config: AppConfig | null = null;

  async getConfig(): Promise<AppConfig> {
    if (this.config) {
      return this.config;
    }

    try {
      const response = await fetch('/config/env.json');
      if (!response.ok) {
        throw new Error(`Failed to load config: ${response.status}`);
      }
      this.config = await response.json();
      return this.config!;
    } catch (error) {
      console.warn('Error loading configuration, using fallback:', error);
      // Fallback configuration for development
      this.config = {
        ADMIN_API: 'http://localhost:14000'
      };
      return this.config;
    }
  }

  async getAdminApiUrl(): Promise<string> {
    const config = await this.getConfig();
    return config.ADMIN_API;
  }
}

export const configService = new ConfigService();
export type { AppConfig };