# Robo-Advisor
The following sections will provide setup instructions and command lines needed to run the program from scratch.

This program allows the user to input stock or cryptocurrency tickers. The program will utilize the Alpha Vantage API to get price data and make a buy  / do not buy recommendation based on the recent high and yesterday's volume. 

The program can handle up to 5 tickers at a time, and will generate price and volume data visualizations to help clarify the recommendation reason. The program will store CSVs of the ticker's data in the "data" directory, and will store the visualizations in the "visualizations" directory.

### Acknowledgments
Based on in class materials from Professor Rossetti. 

## Prerequisites

+ Anaconda 3.7+
+ Python 3.7+
+ Pip

## Setup
Once you have accessed the [repository](https://github.com/sarahmardjuki/robo-advisor) containing the program, "clone" your copy of the remote repository onto your computer. 

Navigate to the local repository's root directory, then navigate using the command line:
```sh
cd robo-advisor
```

Use Anaconda to create and activate a new virtual environment. For example, you can call it "stocks-env":

```sh
conda create -n stocks-env python=3.8 # (first time only)
conda activate stocks-env
```

Once you're inside the virtual environment, install the packages before trying to run the program. 

```sh
pip install -r requirements.txt
```

Now you're ready to use the program! Run the Python script from the command-line:
```sh
python app/robo-advisor.py
```

## Setup: Alpha Vantage API
Visit the [Alpha Vantage website](https://www.alphavantage.co/support/#api-key) to obtain your personal API key. Input your information, then copy the generated API key. 

Create a new file called ".env" in the root directory of your local repository. In this file, create a variable called ALPHAVANTAGE_API_KEY and set it equal to the key.

```sh
ALPHAVANTAGE_API_KEY = "example123"
```


