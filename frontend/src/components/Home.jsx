import React from "react";
import { useEffect, useState } from 'react';
import Box from "./box";
import Graph from "./Graph";

const Home = () => {
    const [investorFullName, setInvestorFullName] = useState("");
    const [weather, setWeather] = useState("");

    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const d = new Date();
    let day = days[d.getDay()];

    const determineTemperature = (degrees_celsius) => {
          if (degrees_celsius < 0) {
               return "❄️";
          }
          if (degrees_celsius > 0 && degrees_celsius < 10) {
               return "🌨️";
          }
          if (degrees_celsius > 10 && degrees_celsius < 20) {
               return "⛅";
          }
          if (degrees_celsius > 20) {
               return "🌤️";
          }
    }

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Get investor name from DB
                const response = await fetch("http://localhost:8000/investors/name/1");
                const nameObj = await response.json();
                const formattedName = `${nameObj.data[0].first_name} ${nameObj.data[0].last_name}`;
                console.log(`Investor name: ${formattedName}`);
                setInvestorFullName(formattedName);

                // Get weather from DB
                const weatherResponse = await fetch(`http://api.weatherapi.com/v1/current.json?key=${import.meta.env.VITE_WEATHER_API}&q=Waterloo`);
                const weatherResponseObj = await weatherResponse.json();
                let temperature = weatherResponseObj.current.temp_c;
                console.log(`Current temperature: ${temperature}`);
                temperature = determineTemperature(temperature);
                setWeather(temperature);
                
            } catch (error) {
                console.error(error);
            }
        };
        fetchData();
    }, []);

    return (
        <div>
            <h1 className='home-header'>Welcome back {investorFullName},</h1>
            <h1 className='home-header-2'>Enjoy your {day} {weather}</h1>
          <div className="main-row">
               <Box></Box>
          </div>  
          <div className="main-row">
               <Graph className="chart"></Graph>
          </div>
        </div>
    );
};

export default Home;
