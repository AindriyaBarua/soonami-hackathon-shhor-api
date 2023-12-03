# ShhorAI - Content Moderation API

## Overview

Welcome to ShhorAI, the premier SaaS API for content moderation, specially tailored for the Indian market. ShhorAI is an AI-powered bot designed to combat hate speech on social media platforms, with a special emphasis on Indian vernacular languages and the safety of marginalized communities. Its advanced algorithms are adept at navigating the complexities of code-mixed language, making it a crucial tool for identifying and mitigating hate speech that traditional tools may overlook.

## Key Features

- **Multilingual Support**: ShhorAI is designed to handle code-mixed language, a common occurrence in India where English and native languages blend.
- **Hate Speech Detection**: The API detects and blurs offensive content, promoting a healthy online environment.
- **Real-time Alerts**: Companies receive real-time alerts, enabling them to make informed decisions about content management.
- **Inclusivity and Safety**: ShhorAI is committed to inclusivity and community safety, making it an indispensable asset for businesses aiming to foster respectful and engaging online spaces.

## Demo Website

We provide a demo website that showcases how ShhorAI can be integrated into a commenting system to detect and mitigate hate speech. The website calls the ShhorAI API each time someone posts a comment, demonstrating the real-time capabilities of the content moderation system.

## API Documentation

### 1. Registration

Before using the ShhorAI API, developers need to register and obtain API credentials.

Endpoint: `/register`


### 2. Token Generation

Once registered, developers can generate an API token for authentication.

Endpoint: `/token`


### 3. Prediction

Use the prediction endpoint to analyze a comment for hate speech.

Endpoint: `/prediction`


### 4. Counting API Calls

To track API usage for cost calculation, use the counting endpoint.

Endpoint: `/user/{username}/request_count`

## Developer

- **CEO and Founder:** Aindriya Barua

## Getting Started

To integrate ShhorAI into your application, follow these steps:

1. Register on the ShhorAI platform to obtain your API credentials.
2. Generate an API token using your credentials.
3. Use the token to make predictions and manage API calls as needed.

For detailed examples and implementation details, refer to the provided demo website code: https://demo.shhorai.com/

## Know More

Please find us at https://www.shhorai.com

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
