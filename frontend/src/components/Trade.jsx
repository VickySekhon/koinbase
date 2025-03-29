import React, { useEffect, useState } from "react";

function Trade() {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [allAssets, setAllAssets] = useState([]);
  const [investorAction, setInvestorAction] = useState("");
  const [quantityPurchased, setQuantityPurchased] = useState(null);
  
  /* const [assetName, setAssetName] = useState("");
  const [exchangeSymbol, setExchangeSymbol] = useState("");
  const [assetPrice, setAssetPrice] = useState(""); */

  useEffect(() => {
    const fetchData = async () => {
      try {
        const assetList = await fetch("http://localhost:8000/all-assets");
        const assetListObj = await assetList.json();
        setAllAssets(assetListObj.data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchData();
  }, []);

  // Handle search
  const handleSearch = (e) => {
    console.log(allAssets);
    console.log(`Search term: ${JSON.stringify(searchTerm)}`);

    if (!searchTerm) {
      console.log(`Empty search, returning...`);
      setSearchResults([]);
      return;
    }

    let results = [];
    for (let asset of allAssets) {
      if (asset.symbol.toLowerCase().includes(searchTerm.toLowerCase())) {
        results.push(asset);
      }
    }

    if (results.length === 0) {
     console.log(`Could not find asset with symbol: ${searchTerm} in database.`);
    }

    setSearchResults(results);
    console.log(searchResults);
  };

  const submitOrder = async () => {
     console.log("submitting order!");
     console.log(`Quantity: ${quantityPurchased}`);
     console.log(`Action: ${JSON.stringify(investorAction)}`);
     console.log(`Asset: ${JSON.stringify(searchResults)}`);

     if (!quantityPurchased || !investorAction || searchResults.length === 0) {
          console.log(`No asset selected or quantity entered or action selected...`);
          return;
     }

     if (Number.isNaN(Number(quantityPurchased))) {
          console.log("Non-numeric quantity entered...");
          return;
     }

     console.log("Executing order now!");
     try {
          const response = await fetch(`http://localhost:8000/execute-order/${investorAction}`);
          const responseObj = await response.json();
          console.log(JSON.stringify(responseObj));
     } catch (error) {
          console.error(error);
     }
     // TODO: NOT WORKING DUE TO CORS ISSUE
     /* try {
          
          let orderDetails = {
               "quantity": quantityPurchased,
               "action": investorAction,
               "account_id": 1,
               "asset": searchResults
          };
          console.log(`VICKY: ${JSON.stringify(orderDetails)}`);
          const response = await fetch("http://localhost:8000/execute-order", {
               method: "POST",
               headers: {
                    "Content-Type": "application/json"
               },
               body: JSON.stringify(orderDetails)
          });
          const responseObj = await response.json();
          console.log(JSON.stringify(responseObj));
     } catch (error) {
          console.error(error);
     } */
  }

  return (
    <div>
      <div className="search-section-trade">
        <input
          type="text"
          placeholder="Lookup an asset... (e.g., AAPL, GOOG, SHOP, MSFT, AMZN, TD, TSLA, META, BNS)"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <button type="submit" onClick={handleSearch} className="search-button">
          GO
        </button>
      </div>
      {searchResults.length > 0 ? (
        <div className="search-results">
          <table>
            <tbody>
              <tr>
                <th>Returned Asset(s)</th>
              </tr>
              <tr>
                <th>
                  {searchResults.map((asset) => {
                    return (
                      <div key={asset.symbol}>
                        <p>{asset.symbol}</p>
                        <p>{asset.exchange_symbol}</p>
                        <p>{asset.price_per_share}</p>
                      </div>
                    );
                  })}
                </th>
              </tr>
            </tbody>
          </table>
        </div>
      ) : (
        <div>No results found...</div>
      )}

      <div className="investor-action">
        <p>Action:</p>
        <select onChange={(e) => setInvestorAction(e.target.value)}>
          <option value=""></option>
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>
      </div>

      <div>
        <p>Quantity:</p>
        <input onChange={(e) => setQuantityPurchased(e.target.value)}>
        </input>
      </div>

      <div className="contains">
          <button className="submit-it" onClick={submitOrder}>Submit Order</button>
      </div>
    </div>
  );
}

export default Trade;
