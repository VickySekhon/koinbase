from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from mysql_connector import Connection, Queries
from contextlib import asynccontextmanager
import json

# Initialize database connection and query executor
connection = None
queries = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for database connection"""
    # Startup code
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    global connection, queries
    connection = Connection(
        os.getenv("DB_HOST"),
        os.getenv("DB_NAME"),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD")
    )
    
    if connection.connect():
        queries = Queries(connection)
    else:
        raise Exception("Failed to connect to the database")
    
    yield
    
    # Shutdown code
    if connection:
        connection.disconnect()

app = FastAPI(title="Koinbase API", description="Investment Database API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Koinbase API", "status": "online"}



# * Home Page Endpoints *
@app.get("/investors/name/{investor_id}")
async def get_investor_name(investor_id: int):
    result = queries.getInvestorName(investor_id)
    return format_result(result)

@app.get("/investors/portfolio-value/{account_id}")
async def get_portfolio_value(account_id: int):
    result = queries.getPortfolioValue(account_id)
    return format_result(result)

@app.get("/investors/portfolio-return/{account_id}")
async def get_portfolio_return(account_id: int):
    result = queries.getPortfolioReturn(account_id)
    return format_result(result)

@app.get("/investors/available-funds/{investor_id}")
async def get_investor_funds(investor_id: int):
    result = queries.getInvestorFunds(investor_id)
    return format_result(result)

@app.get("/all-assets")
async def get_all_assets():
    result = queries.getAllAssets()
    return format_result(result)

@app.get("/execute-order/{investorAction}")
async def execute_order(investorAction: str):
    # Simulating backend data retrieval
    body = {
        "quantity": 12,
        "action": investorAction,
        "account_id": "1",
        "asset_id": 1,
        "price_per_share": 333.505
    }

    asset_quantity = body["quantity"]
    transaction_type = body["action"]
    account_id = body["account_id"]
    asset_id = body["asset_id"]
    price_per_share = body["price_per_share"]

    print(asset_quantity)
    print(transaction_type)
    print(asset_id)
    print(price_per_share)
    print(account_id)

    if transaction_type == "buy":
        result = queries.executeBuy(account_id, asset_id, asset_quantity, price_per_share)
    else:
        result = queries.executeSell(account_id, asset_id, asset_quantity, price_per_share)

    return {"successfully_completed": result}

# TODO: FIX BACKEND ISSUE WHEN SUBMITTING ORDER
""" @app.post("/execute-order")
async def execute_order(request: Request):
    body = await request.json()
    print(body)
    
    # Accessing dictionary keys with [] notation
    asset_quantity = body["quantity"]
    transaction_type = body["action"]
    account_id = body["account_id"]
    asset_id = body["asset"][0]["asset_id"]
    price_per_share = body["asset"][0]["asset_id"]
    
    print(asset_quantity)
    print(transaction_type)
    print(asset_id)
    print(price_per_share)
    print(account_id)
    
    if transaction_type == "buy":
        result = queries.executeBuy(account_id, asset_id, asset_quantity, price_per_share);
    else:
        result = queries.executeSell(account_id, asset_id, asset_quantity, price_per_share);
        
    return { "successfully_completed": result } """

# * Research Page Endpoints *
# === Investor Endpoints ===
@app.get("/investors/quartiles")
async def get_investors_by_quartile():
    """Get investors divided into quartiles based on funds"""
    result = queries.groupInvestorsByAvailableFunds()
    return format_result(result)

@app.get("/investors/above-average")
async def get_investors_above_avg_funds():
    """Get investors with above-average funds"""
    result = queries.investorsWithAboveAverageFunds()
    return format_result(result)

@app.get("/investors/by-occupation")
async def get_funds_by_occupation():
    """Get total funds by occupation"""
    result = queries.fundsAvailableByOccupation()
    return format_result(result)

@app.get("/investors/portfolio-ranks")
async def get_investor_portfolio_ranks():
    """Get ranked portfolios by value"""
    result = queries.rankInvestorPortfolios()
    return format_result(result)

@app.get("/investors/high-value-portfolios")
async def get_high_value_portfolios():
    """Get highest portfolio value"""
    result = queries.getHighestAmountInvested()
    return format_result(result)

@app.get("/investors/total-investment")
async def get_total_investment():
    """Get total amount invested across all users"""
    result = queries.getTotalAmountInvested()
    return format_result(result)

@app.get("/investors/portfolio-return/{account_id}")
async def get_portfolio_return(account_id: int):
    """Get portfolio return for a specific account"""
    result = queries.getPortfolioReturn(account_id)
    return format_result(result)

@app.get("/investors/portfolio-coordinates/{account_id}")
async def get_portfolio_coordinates(account_id: int):
    """Get portfolio coordinates for charting"""
    result = queries.getXYCoordinates(account_id)
    return format_result(result)

@app.get("/investors/age-account")
async def get_investors_by_age_account():
    """Get investors by age and account type"""
    result = queries.commonInvestorAccountsByAge()
    return format_result(result)

# === Analytics Endpoints ===
@app.get("/analytics/popular-account-asset")
async def get_popular_account_asset():
    """Find most popular account and asset"""
    result = queries.mostTrendingInvestmentAccount()
    return format_result(result)

@app.get("/analytics/trending-buy")
async def get_trending_buy():
    """Get most trending buy"""
    result = queries.mostTrendingBuy()
    return format_result(result)

@app.get("/analytics/transaction-city-rank")
async def get_transaction_city_rank():
    """Get city ranking by transaction counts"""
    result = queries.cityWithMostTransactions()
    return format_result(result)

@app.get("/analytics/price-alerts")
async def get_price_alerts():
    """Get assets that have fallen below target price"""
    result = queries.getPriceBelowTarget()
    return format_result(result)

# === Transaction Endpoints ===
@app.post("/transactions/buy")
async def execute_buy(account_id: int, asset_id: int, asset_quantity: int, price_per_share: float):
    """Execute a buy transaction"""
    result = queries.executeBuy(account_id, asset_id, asset_quantity, price_per_share)
    return {"success": result}

@app.post("/transactions/sell")
async def execute_sell(account_id: int, asset_id: int, asset_quantity: int, price_per_share: float):
    """Execute a sell transaction"""
    result = queries.executeSell(account_id, asset_id, asset_quantity, price_per_share)
    return {"success": result}

def format_result(result):
    """Format the query result to a standardized response format"""
    if result == "No results found":
        return {"data": [], "message": "No results found"}
    
    return {"data": result}
