import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '..', '.env') });

export const URLS = {
  qa:{
    HHH: "https://qa.kinnser.net/"
  }
}

export const Credentials = {
  qa: {
    username: process.env.USER_NAME,
    password: process.env.PASSWORD
  }
}
