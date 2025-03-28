import { useState, useEffect } from 'react';
import '../App.css';

const Research = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [trendingAsset, setTrendingAsset] = useState(null);
  const [totalInvestment, setTotalInvestment] = useState(null);
  const [portfolioReturn, setPortfolioReturn] = useState(null);
  const [priceAlerts, setPriceAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // List of available assets for search
  const availableAssets = [
    { symbol: 'AAPL', name: 'Apple Inc.', exchange: 'NASDAQ', price: 333.33 },
    { symbol: 'GOOG', name: 'Alphabet Inc.', exchange: 'NASDAQ', price: 164.08 },
    { symbol: 'SHOP', name: 'Shopify Inc.', exchange: 'NYSE', price: 146.62 },
    { symbol: 'MSFT', name: 'Microsoft Corporation', exchange: 'NASDAQ', price: 390.58 },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', exchange: 'NASDAQ', price: 201.36 },
    { symbol: 'TD', name: 'Toronto-Dominion Bank', exchange: 'NYSE', price: 87.29 },
    { symbol: 'TSLA', name: 'Tesla Inc.', exchange: 'NASDAQ', price: 273.13 },
    { symbol: 'META', name: 'Meta Platforms Inc.', exchange: 'NASDAQ', price: 602.58 },
    { symbol: 'BNS', name: 'Bank of Nova Scotia', exchange: 'NYSE', price: 69.20 }
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch trending asset
        const trendingResponse = await fetch('http://localhost:8000/analytics/trending-buy');
        const trendingData = await trendingResponse.json();
        setTrendingAsset(trendingData?.data && trendingData.data.length > 0 ? trendingData.data[0] : null);

        // Fetch total investment
        const investmentResponse = await fetch('http://localhost:8000/investors/total-investment');
        const investmentData = await investmentResponse.json();
        setTotalInvestment(investmentData?.data && investmentData.data.length > 0 ? investmentData.data[0] : null);

        // For portfolio return, we'd need an account ID - using 1 as default
        const returnResponse = await fetch('http://localhost:8000/investors/portfolio-return/1');
        const returnData = await returnResponse.json();
        setPortfolioReturn(returnData?.data && returnData.data.length > 0 ? returnData.data[0] : null);

        // Fetch price alerts
        const alertsResponse = await fetch('http://localhost:8000/analytics/price-alerts');
        const alertsData = await alertsResponse.json();
        setPriceAlerts(alertsData?.data ? alertsData.data : []);

        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch data. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchTerm) {
      setSearchResults([]);
      return;
    }

    const results = availableAssets.filter(asset => 
      asset.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setSearchResults(results);
  };

  return (
    <div className="research-container">
      <h1>Research</h1>
      
      {/* Search Section */}
      <div className="search-section">
        <h2>Asset Lookup</h2>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Lookup an asset... (e.g., AAPL, GOOG, SHOP, MSFT, AMZN, TD, TSLA, META, BNS)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">GO</button>
        </form>
        
        {searchResults.length > 0 && (
          <div className="search-results">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>Exchange</th>
                  <th>Price</th>
                </tr>
              </thead>
              <tbody>
                {searchResults.map((asset) => (
                  <tr key={asset.symbol}>
                    <td>{asset.symbol}</td>
                    <td>{asset.name}</td>
                    <td>{asset.exchange}</td>
                    <td>${asset.price.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* Trending Asset Section */}
      <div className="trending-section">
        <h2>Most Popular Asset</h2>
        {loading ? (
          <p>Loading trending asset data...</p>
        ) : error ? (
          <p className="error">{error}</p>
        ) : trendingAsset ? (
          <div className="trending-asset">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Price</th>
                  <th>Trade Volume</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{trendingAsset.symbol || 'APPL'}</td>
                  <td>${trendingAsset.price || '333'}</td>
                  <td>{trendingAsset.volume || '2'}</td>
                </tr>
              </tbody>
            </table>
          </div>
        ) : (
          <p>No trending asset data available</p>
        )}
      </div>
      
      {/* Market Data Section */}
      <div className="market-data-section">
        <h2>Market Insights</h2>
        {loading ? (
          <p>Loading market data...</p>
        ) : error ? (
          <p className="error">{error}</p>
        ) : (
          <>
            <div className="market-summary">
              <div className="summary-card">
                <h3>Total Investment</h3>
                <p className="data-value">
                  {totalInvestment?.total_amount_invested_across_all_portfolios || '$0'}
                </p>
              </div>
              
              <div className="summary-card">
                <h3>Portfolio Return (ID: 1)</h3>
                <p className="data-value">
                  {portfolioReturn?.portfolio_returns || '0%'}
                </p>
              </div>
            </div>
            
            <div className="price-alerts">
              <h3>Price Alerts</h3>
              {priceAlerts.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      <th>Asset</th>
                      <th>Current Price</th>
                      <th>Target Price</th>
                      <th>Difference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {priceAlerts.map((alert, index) => (
                      <tr key={index}>
                        <td>{alert.symbol || 'Unknown'}</td>
                        <td>${alert.price_per_share || 0}</td>
                        <td>${alert.target_price || 0}</td>
                        <td className="price-diff negative">
                          {alert.price_per_share && alert.target_price 
                            ? `${(((alert.price_per_share - alert.target_price) / alert.target_price) * 100).toFixed(2)}%` 
                            : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No price alerts available</p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Research; 