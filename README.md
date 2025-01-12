# Deal Predator

**Deal Predator** is a customizable price tracker that allows users to set target prices and receive notifications via Telegram. The application uses web scraping to monitor prices on e-commerce websites, providing a simple and efficient solution for bargain hunters.

## Features

- **Customizable Targets**: Set specific price targets for your favorite products.
- **Real-Time Notifications**: Receive instant updates via Telegram when prices hit your target.
- **Web Scraping**: Uses Selenium WebDriver to scrape product data from e-commerce websites.
- **Dashboard**: Simple and intuitive HTML/CSS-based dashboard for tracking targets and viewing updates.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML templates with CSS
- **Database**: SQLite
- **Web Scraping**: Selenium WebDriver
- **Notifications**: Telegram Bot API

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/deal-predator.git
   cd deal-predator
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the Telegram bot:
   - Create a Telegram bot using BotFather and get your bot token.
   - Update the configuration file or environment variables with the bot token.

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the dashboard:
   Open your browser and navigate to `http://localhost:5000`.

## Usage

1. Add products to track and set price targets using the dashboard.
2. The system will monitor the prices periodically.
3. Receive Telegram notifications when the prices drop to your target.

## Contribution

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or feature requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
