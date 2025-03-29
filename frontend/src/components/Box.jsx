import React, { useEffect, useState } from "react";

function Box() {

     const [portfolioValue, setPortfolioValue] = useState(null);
     const [totalReturnsValue, setTotalReturnsValue] = useState(null);
     const [availableFundsValue, setAvailableFundsValue] = useState(null);

     useEffect(() => {
          const fetchData = async () => {
               try {
                    // Total portfolio value
                    const portfolioValue = await fetch("http://localhost:8000/investors/portfolio-value/1");
                    const portfolioValueObj = await portfolioValue.json();
                    console.log(`Portfolio value: ${portfolioValueObj.data[0].total_portfolio_value}`);
                    setPortfolioValue(portfolioValueObj.data[0].total_portfolio_value);

                    // Total portfolio returns
                    const portfolioReturns = await fetch("http://localhost:8000/investors/portfolio-return/1");
                    const portfolio_returnsObj = await portfolioReturns.json();
                    console.log(`Portfolio returns: ${portfolio_returnsObj.data[0].portfolio_returns}`);
                    setTotalReturnsValue(portfolio_returnsObj.data[0].portfolio_returns);

                    // Total investor funds available
                    const investorFunds = await fetch("http://localhost:8000/investors/available-funds/1");
                    const investorFundsObj = await investorFunds.json();
                    console.log(`Available funds: ${investorFundsObj.data[0].funds}`);
                    setAvailableFundsValue(investorFundsObj.data[0].funds);
               } catch (error) {
                    console.error(error);
               }
          } 
          fetchData();
     }, [])

     return <div>
          <table className="portfolio-overview">
               <th className="overview-title">Your Personalized Overview:</th>
               <tbody>
               <tr>
                    { portfolioValue ? (
                         <th>Portfolio Value: {portfolioValue}</th>
                    ) : (
                         <th>Loading portfolio data...</th>
                    )}
               </tr>
               <tr>
                    { totalReturnsValue ? (
                         <th>Total Returns: {totalReturnsValue}</th>
                    ) : (
                         <th>Loading total returns data...</th>
                    )}
               </tr>
               <tr>
                    { availableFundsValue ? (
                         <th>Available Funds: {availableFundsValue}</th>
                    ) : (
                         <th>Loading available funds data...</th>
                    )}
               </tr>
               </tbody>
          </table>
     </div>
}

export default Box;