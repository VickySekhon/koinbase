import mysql.connector
import os
from dotenv import load_dotenv
from tabulate import tabulate
load_dotenv()

# TODO: Change code to prevent SQL injection

class Queries:
     
     def __init__(self, connection):
          self.connection = connection


     # * 9 Simple Queries *
     
     # Query 1. Find all investors to send updates to for when an asset falls below their target_price
     def getPriceBelowTarget(self):
          return self.connection.executeQuery(f"""
          select w.investor_id, a.symbol, w.target_price, ap.price_per_share
          from Watchlists w
          join Assets a on a.asset_id = w.asset_id
          join Asset_Prices ap on ap.asset_id = a.asset_id
          where ap.price_per_share <= w.target_price;
          """)
          
     # Query 2. (x,y) coordinates for an investor's portfolio so that it can be plotted with Chart.js
     def getXYCoordinates(self, account_id):
          return self.connection.executeQuery(f"""
          SELECT DISTINCT pp.current_price AS y, ROW_NUMBER() OVER (ORDER BY p.performance_date ASC) AS x 
          FROM Performances p
          JOIN Performance_Prices pp ON pp.account_id = p.account_id 
          AND pp.performance_date = p.performance_date
          WHERE p.account_id = {account_id};
          """)
     
     # Query 3. The portfolio return for a single portfolio
     def getPortfolioReturn(self, account_id):
          return self.connection.executeQuery(f"""
          SELECT CONCAT(FORMAT(ROUND(((p.current_price - ip.initial_price)/ip.initial_price) * 100, 3), 3), '%') AS portfolio_returns
          FROM Performance_Prices p
          JOIN Initial_Prices ip ON ip.account_id = p.account_id
          WHERE p.account_id = {account_id}
          ORDER BY p.performance_date DESC
          LIMIT 1;
          """)

     # Query 4. Total amount invested across all users
     def getTotalAmountInvested(self):
          return self.connection.executeQuery(f"""
          SELECT CONCAT('$', FORMAT(SUM(p.asset_quantity * ap.price_per_share), 2)) AS total_amount_invested_across_all_portfolios
          FROM Portfolios p
          JOIN Assets a ON p.asset_id = a.asset_id
          JOIN Asset_Prices ap ON ap.asset_id = a.asset_id;
          """)

     # Query 5. The highest amount invested across all portfolios
     def getHighestAmountInvested(self):
          return self.connection.executeQuery(f"""
          SELECT 
          CONCAT('$', FORMAT(ROUND(MAX(total_portfolio_value), 2), '###,###.##')) AS highest_portfolio_value
          FROM (
          SELECT 
               account_id, 
               SUM(asset_quantity * price_per_share) AS total_portfolio_value
          FROM Portfolios
          JOIN Assets ON Portfolios.asset_id = Assets.asset_id
          JOIN Asset_Prices ON Assets.asset_id = Asset_Prices.asset_id
          GROUP BY account_id
          ) AS account_portfolios;
          """)

     #  Query 6. Divide investors into 4 groups based on the amount of funds they have
     def groupInvestorsByAvailableFunds(self):
          return self.connection.executeQuery(f"""
          SELECT investor_id, first_name, last_name, funds,
               NTILE(4) OVER (ORDER BY funds DESC) AS fund_quartile
          FROM Investors;
          """)
     
     # Query 7. Investors who have more funds than the average investor
     def investorsWithAboveAverageFunds(self):
          return self.connection.executeQuery(f"""
          SELECT investor_id, first_name, last_name, funds
          FROM Investors
          WHERE funds > (SELECT AVG(funds) FROM Investors)
          ORDER BY funds DESC;
          """)

     # Query 8. Funds deposited into each investors account by occupation
     def fundsAvailableByOccupation(self):
          return self.connection.executeQuery(f"""
          SELECT occupation, funds AS total_funds
          FROM Investors
          GROUP BY occupation
          ORDER BY total_funds DESC;
          """)

     # Query 9. CTE (common table expression) to get total amount of investors' portfolios and rank them based on the total value across all their portfolios
     def rankInvestorPortfolios(self):
          return self.connection.executeQuery(f"""
          with Portfoliovalues as ( 
          SELECT 
               account_id, 
               SUM(asset_quantity * price_per_share) AS total_portfolio_value
          FROM Portfolios
          JOIN Assets ON Portfolios.asset_id = Assets.asset_id
          JOIN Asset_Prices ON Assets.asset_id = Asset_Prices.asset_id
          GROUP BY account_id
          )
          Select i.investor_id, i.first_name, i.last_name, CONCAT('$', FORMAT(ROUND(pv.total_portfolio_value, 2), '###,###.##')) as funds, 
               Rank() Over (order by pv.total_portfolio_value desc) As fund_rank
          From Investors i
          join Accounts a on a.investor_id = i.investor_id
          join Portfoliovalues pv on pv.account_id = a.account_id
          Order by fund_rank;
          """)
          
     # * 4 Complex Queries *
     
     # Advanced query 1. Find the most popular account and the most commonly held asset within that account
     def mostTrendingInvestmentAccount(self):
          return self.connection.executeQuery(f""" 
          select a_type.account_type, COUNT(*) As count, asst.symbol
          from Accounts a
          join Account_Types a_type on a_type.account_type_id = a.account_type_id
          join Portfolios p on p.account_id = a.account_id
          join Assets asst on p.asset_id = asst.asset_id
          group by a.account_type_id
          order by count desc
          limit 1;
          """)
     
     # Advanced query 2. Most trending buy right now
     def mostTrendingBuy(self):
          return self.connection.executeQuery(f""" 
          select a.symbol, ap.price_per_share, count(a.asset_id) as "Trade_volume" from Carts c
          join Assets a on a.asset_id = c.asset_id
          join Asset_Prices ap on ap.asset_id = a.asset_id
          group by a.asset_id
          order by Trade_volume desc
          limit 1;
          """)
     
     # Advanced query 3. City of investors who are making the most transactions
     def cityWithMostTransactions(self):
          return self.connection.executeQuery(f""" 
          SELECT 
               SUBSTRING_INDEX(SUBSTRING_INDEX(i.home_address, ',', 2), ',', -1) AS city, -- 1st substring_index gives ("street", "city"), 2nd gives ("city")
               COUNT(t.transaction_id) AS transaction_count,
               RANK() OVER (ORDER BY COUNT(t.transaction_id) DESC) AS transaction_rank
          FROM Investors i
          JOIN Accounts a ON a.investor_id = i.investor_id
          JOIN Transactions t ON t.account_id = a.account_id
          GROUP BY i.home_address, i.investor_id, a.account_id
          ORDER BY transaction_rank;
          """)
     
     # Advanced query 4. Number of investors with accounts grouped by age and account_type
     def commonInvestorAccountsByAge(self):
          return self.connection.executeQuery(f"""
          SELECT 
               TIMESTAMPDIFF(YEAR, i.date_of_birth, CURDATE()) AS age, 
               i.date_of_birth,
               atype.account_type,
               COUNT(*) AS num_investors
          FROM Investors i
          JOIN Accounts a ON a.investor_id = i.investor_id
          JOIN Account_Types atype ON a.account_type_id = atype.account_type_id
          GROUP BY age, atype.account_type
          ORDER BY age DESC;
          """)
     
     # * Fundamental Business Logic Actions *
     
     def validateBuyOrder(self, account_id, cost):
          """
          Validates that an Investor has sufficient funds to purchase an asset.

          Parameters:
          account_id (int): Investor's account_id
          cost (float) = PPS x quantity
          
          Returns:
          True (bool) - Able to validate buy order
          False (bool) - Unable to validate buy order
          """
          validFunds = self.connection.executeQuery(f"select funds from Accounts a join Investors i on i.investor_id = a.investor_id where funds >= {cost} and account_id = {account_id};")
          
          if validFunds == "No results found":
               print(f"Account: {account_id} does not have sufficient funds to purchase asset (funds < ${cost}).")
               return False
          
          return True
          
     
     def validateSellOrder(self, account_id, asset_id, asset_quantity):
          """
          Validates that an Investor has sufficient assets to sell.

          Parameters:
          account_id (int): Investor's account_id
          asset_id (int): Id of the asset that the Investor wants to sell
          asset_quantity (int): Quantity of the asset that the Investor wants to sell
          
          Returns:
          True (bool) - Able to validate sell order
          False (bool) - Unable to validate sell order
          """
          # Case #1: Investor doesn't own the asset
          assetExists = self.connection.executeQuery(f"select * from Portfolios where account_id = {account_id} and asset_id = {asset_id};")
          
          # Case #2: Investor owns the asset but less than the amount to sell
          validQuantity = self.connection.executeQuery(f"select * from Portfolios where account_id = {account_id} and asset_id = {asset_id} and asset_quantity >= {asset_quantity};")
          
          if assetExists == "No results found" or validQuantity == "No results found":
               if assetExists == "No results found": print(f"Account: {account_id} does not own the asset: {asset_id}")
               else: print(f"Account: {account_id} does not have: {asset_quantity} shares of the asset: {asset_id}")
               return False
          
          return True
     
     def subtractFundsFromAccount(self, account_id, cost):
          # Deduct the cost from the Investor's total funds
          self.connection.executeQuery(f"""UPDATE Investors i
                                           JOIN Accounts a ON i.investor_id = a.investor_id
                                           SET i.funds = i.funds - {cost}
                                           WHERE a.account_id = {account_id};""");
          
          updatedBalance = self.connection.executeQuery(f"""select funds from Investors i join Accounts a on i.investor_id = a.investor_id where a.account_id = {account_id}""")[0]['funds']
          print(f"Account: {account_id} now has a balance of: ${updatedBalance}.")
     
     def addTransactionRecord(self, account_id, asset_id, asset_quantity, transaction_type):
          self.connection.executeQuery(f"""
          insert into Transactions (account_id, asset_id, asset_quantity, transaction_time, transaction_type)
          VALUES ({account_id}, {asset_id}, {asset_quantity}, NOW(), {transaction_type});
          """)
     
     def removeItemFromCart(self, account_id, asset_id):
          self.connection.executeQuery(f"""
          delete from Carts
          where account_id = {account_id} and asset_id = {asset_id};
          """)
     
     def updatePortfolioQuantity(self, account_id, asset_id, new_asset_quantity, add: bool):           
          self.connection.executeQuery(f"""
          INSERT INTO Portfolios (account_id, asset_id, asset_quantity)
          VALUES ({account_id}, {asset_id}, {new_asset_quantity})
          ON DUPLICATE KEY UPDATE 
          asset_quantity = asset_quantity {"+" if add else "-"} {new_asset_quantity};
          """)
     
     def addNewPerformanceEntry(self, account_id, time=None):
          self.connection.executeQuery(f"""
          INSERT INTO Performances (account_id, performance_date) 
          ({account_id}, {time if time else "NOW()"})
          """)
          
     def updatePerformancePriceEntry(self, account_id, price_per_share, asset_quantity, add: bool, time=None):
          self.connection.executeQuery(f"""          
          INSERT INTO Performance_Prices (account_id, performance_date, current_price) 
          SELECT account_id, {time if time else "NOW()"}, current_price {"+" if add else "-"} ({price_per_share}*{asset_quantity})
          FROM Performance_Prices
          WHERE account_id = {account_id}
          ORDER BY performance_date DESC
          LIMIT 1;
          """)
     
     def getInvestorName(self, investor_id):
          return self.connection.executeQuery(f"""select first_name, last_name from Investors where investor_id = {investor_id};""")
     
     def getPortfolioValue(self, account_id):
          return self.connection.executeQuery(f"""
          SELECT CONCAT('$', FORMAT(SUM(p.asset_quantity * ap.price_per_share), 2)) AS total_portfolio_value
          FROM Portfolios p
          JOIN Assets a ON p.asset_id = a.asset_id
          JOIN Asset_Prices ap ON ap.asset_id = a.asset_id
          where account_id = {account_id}; 
          """);
          
     def getInvestorFunds(self, investor_id):
          return self.connection.executeQuery(f"""
          SELECT CONCAT('$', FORMAT(funds, 2)) AS funds
          FROM Investors
          WHERE investor_id = {investor_id};
          """)
          
     def getAllAssets(self):
          return self.connection.executeQuery(f"""select A.asset_id, A.symbol, E.exchange_symbol, AP.price_per_share from Assets A join Asset_Prices AP on A.asset_id = AP.asset_id join Exchanges E on A.exchange_id = E.exchange_id;""");

     def executeBuy(self, account_id, asset_id, asset_quantity, price_per_share, transaction_type="Buy"):
          """
          Performs a "Buy" order.
          
          Steps to take:
          1. Add a sell transaction record
          2. Empty the Investor's cart
          3. Update the Investor's portfolio quantity
          4. Add a performance entry to track change in value

          Parameters:
          account_id (int): Investor's account_id
          asset_id (int): Id of the asset that the Investor wants to buy
          asset_quantity (int): Quantity of the asset that the Investor wants to buy
          price_per_share (int): PPS of the asset that the Investor is buying at
          transaction_type (str): "Buy"
          
          Returns:
          True (bool) - Successfully completed the buy order
          False (bool) - Unable to complete the buy order
          """
          # Check that the Investor has sufficient funds to buy
          cost = price_per_share * asset_quantity
          validOrder = self.validateBuyOrder(account_id, cost)
          if not validOrder:
               print(f"Invalid BUY order -> the Investor with account_id: {account_id} does not have sufficient funds to purchase {asset_quantity} shares of asset: {asset_id} whose cost is: {cost}.")
               return False
          
          self.connection.executeQuery(self.addTransactionRecord(account_id, asset_id, asset_quantity, transaction_type))
          self.connection.executeQuery(self.removeItemFromCart(account_id, asset_id))
          self.connection.executeQuery(self.updatePortfolioQuantity(account_id, asset_id, asset_quantity, True))
          
          # Time will be off by a millisecond between the two queries below, get the time now and set it once for consistency
          time = self.connection.executeQuery("SELECT NOW()")
          self.connection.executeQuery(self.addNewPerformanceEntry(account_id, time))
          self.connection.executeQuery(self.updatePerformancePriceEntry(account_id, price_per_share, asset_quantity, True, time))
          
          # Deduct from their available funds
          self.subtractFundsFromAccount(account_id, cost)
          return True
          

     def executeSell(self, account_id, asset_id, asset_quantity, price_per_share, transaction_type="Sell"):
          """
          Performs a "sell" order.
          
          Steps to take:
          1. Add a sell transaction record
          2. Empty the Investor's cart
          3. Update the Investor's portfolio quantity
          4. Add a performance entry to track change in value

          Parameters:
          account_id (int): Investor's account_id
          asset_id (int): Id of the asset that the Investor wants to sell
          asset_quantity (int): Quantity of the asset that the Investor wants to sell
          price_per_share (int): PPS of the asset that the Investor is selling at
          transaction_type (str): "Sell"
          
          Returns:
          True (bool) - Successfully completed the sell order
          False (bool) - Unable to complete the sell order
          """
          # Check to ensure that they own the asset before they sell
          validOrder = self.validateSellOrder(account_id, asset_id, asset_quantity)
          if not validOrder:
               print(f"Invalid SELL order -> the Investor with account_id: {account_id} does not own asset_id: {asset_id} or has an insufficient quantity to sell.")
               return False
          
          self.connection.executeQuery(self.addTransactionRecord(account_id, asset_id, asset_quantity, transaction_type))
          self.connection.executeQuery(self.removeItemFromCart(account_id, asset_id))
          self.connection.executeQuery(self.updatePortfolioQuantity(account_id, asset_id, asset_quantity, False))
          
          # Time will be off by a millisecond between the two queries below, get the time now and set it once for consistency
          time = self.connection.executeQuery("SELECT NOW()")
          self.connection.executeQuery(self.addNewPerformanceEntry(account_id, time))
          self.connection.executeQuery(self.updatePerformancePriceEntry(account_id, price_per_share, asset_quantity, False, time))
          return True



class Connection:
     
     def __init__(self, host, database, userName, password):
          self.host = host
          self.database = database
          self.userName = userName
          self.password = password
          self.connection = None

     def connect(self):
          try:
               self.connection = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.userName,
                    password=self.password
               )
               if self.connection.is_connected():
                    return True
          except Error as e:
               print(f"Error connecting to MySQL database: {e}")
               return False
          return False
     
     def disconnect(self):
          if self.connection and self.connection.is_connected():
               self.connection.close()
               print("Database connection closed.")
     
     def executeQuery(self, query):
          cursor = self.connection.cursor(dictionary=True)
          cursor.execute(query)
          result = cursor.fetchall()
          cursor.close()
          #return result if result else "No results found"
          return result if result else "No results found"
          return tabulate(result) if result else "No results found"

def main():
     connection = Connection(
          os.getenv("DB_HOST"),
          os.getenv("DB_NAME"),
          os.getenv("DB_USER"),
          os.getenv("DB_PASSWORD")
     )

     if not connection.connect():
          return  # Exit if connection fails

     queries = Queries(connection) # pass connection object to Queries class
     
#    output = queries.validateSellOrder(1, 2, 30)
#    output = connection.executeQuery("select NOW()")
#    output = connection.executeQuery("select funds from Accounts a join Investors i on i.investor_id = a.investor_id where account_id = 2;")
#    output = connection.executeQuery(f"""select funds from Investors i join Accounts a on i.investor_id = a.investor_id where a.account_id = 2""")[0]['funds']
     #output = queries.cityWithMostTransactions()
     output = queries.getInvestorName(1)
     print(f"\nOutput:\n{output}\n")
     connection.disconnect()

if __name__ == "__main__":
     main()