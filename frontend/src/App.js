import logo from './logo.svg';
import './App.css';
import Chart from "./Chart"
import PerformanceChart from './PerformanceChart';
import BarChart from "./BarChart"
import PriceChart from "./PriceChart"
import styled from "styled-components";
import React, {useRef, useEffect, useState} from 'react';
import {ethers} from 'ethers'
import $, { data } from 'jquery'

import Button from '@mui/material/Button';
import { InlineIcon } from '@iconify/react';

import { letterFrequency } from '@visx/mock-data';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleLinear, scaleBand } from '@visx/scale';
// import * as d3 from 'd3'
import { select, csv, line, curveCardinal, timeFormat, timeParse } from "d3";
// import TextField from "@material-ui/core/TextField";
// import { makeStyles } from "@material-ui/core/styles";
// import { FormControl, FormControlLabel, FormLabel, Radio, RadioGroup } from '@material-ui/core';

// const useStyles = makeStyles((theme) => ({
// 	root: {
// 	  "& > *": {
// 		margin: theme.spacing(1),
// 	  },
// 	},>
//    }));

const Container = styled.div`
	background-color: #506B80;
	width: 57%;
	min-width: 600px;
	max-width: 1000px;
	height: 15%;
	min-height: 350px;
	max-height: 400px;
	border-radius: 40px;
	position: relative;
	overflow: hidden
`;

// width: 900px; height: 400px;
// min-width: 300px;
// background-color: #201d47; - purplish

const App = () => {
	const [stratData, setStratData] = useState([])
	const [perfData, setPerfData] = useState([])
	const [perfLoading, setPerfLoading] = useState(true)
	const [dataLoading, setDataLoading] = useState(true)
	const [dataCount, setDataCount] = useState(400) // Data Count should probably be set somewhere better
	const [message, setMessage] = useState([{}])
	const [balance, setBalance] = useState()
	const [profit, setProfit] = useState(0)
	const [count, setCount] = useState(0)
	const [intervalStarted, setIntervalStarted] = useState(false)
	const [openButtonText, setOpenButtonText] = useState('Check Faster!')
	const [defaultAccount, setDefaultAccount] = useState(null);
	const [connButtonText, setConnButtonText] = useState('Connect Wallet');
	const [errorMessage, setErrorMessage] = useState(null);
	const [provider, setProvider] = useState(null);
	const [signer, setSigner] = useState(null);
	const [admin, setAdmin] = useState(false);

	const [ruleColor, setRuleColor] = useState("#a7a7a7")	
	const [currDiff, setCurrDiff] = useState(0)

	const startingBal = 173.6 
	const startingPrice = 1895.41 
	const grayColor = "#a7a7a7" // grey - no particular meaning
	const downColor = "#ff9c92"
	const upColor = "#329067"
	

	$.ajaxSetup({
		crossDomain: true
	})
	const query = async () => {
		var request = '/data' // This should be passed in as an arg
		var uri = 'http://75.142.245.55:8080' + request
		var res = $.getJSON(uri, function(data){
			setBalance(((data.active_bal * data.Close) + data.usd_bal).toFixed(2))
			setProfit((((((data.active_bal * data.Close) + data.usd_bal)/startingBal)-1)*100).toFixed(2)) // This uses a hard-coded starting value
			setMessage(data)
		})
		setTimeout(query,5000)
	}

	const get_strategy_data = () => {
        csv('http://box.zzimm.com:8080/strategy_data').then( async (d) => {
            await Promise.all(d.map(async(d) => {
                if(d['dev_sma'] === ""){ d['dev_sma'] = 0}
                if(d['dev_sma'] === "NaN"){ d['dev_sma'] = 0}
                if(d['dev_dir'] === ""){ d['dev_dir'] = 0}
                if(d['d'] === ""){ d['d'] = 0}
                let new_date = d['Date'].split('.')[0]
                d['Date'] = new_date
                d['dev_sma'] = Number(d['dev_sma'])
                d['d'] = Number(d['dev_dir'])
                d['dev_dir'] = Number(d['dev_dir'])
								d['sma_for_dev'] = Number(d['sma_for_dev'])
                d['dev_upper'] = Number(d['dev_upper'])
                d['dev_lower'] = Number(d['dev_lower'])
                d['Close'] = Number(d['Close'])
                d['dev'] = Number(d['dev'])
                d['0'] = 0
                d['y'] = d['Close']
				// return d
            }))
            setStratData(d.slice(-1 * dataCount))
            setDataLoading(false)
            setTimeout(get_strategy_data,150000) // Check for new data in 2.5 minutes and cause chart to re-render
        })
    }



	const set_rule_color = () => {
		if(message.Close > message.prev_close) { 
			setRuleColor(upColor)
		}
		else if (message.Close < message.prev_close){ 
			setRuleColor(downColor) 
		}
		else { 
			setRuleColor(grayColor) }
	}

	const get_performance_data =  () => {
        var current = new Date()
        var dateEntry = current.getFullYear() + "-" +
                    (current.getUTCMonth()+1) + "-" + 
                    current.getUTCDate() + " " +
                    current.getUTCHours() + ":" +
                    current.getMinutes() + ":" +
                    current.getSeconds() + "." +
                    current.getMilliseconds()
        var new_entry = {
            Date: dateEntry, 
            price: message.Close,
            balance: (message.active_bal * message.Close) + message.usd_bal
        }

				        csv('http://75.142.245.55:8080/strategy_log').then( async (d) => {
            await Promise.all(d.map((d) => {
                let new_date = (d['Date'].split('.')[0])
                d['Date'] = new_date
                d['price'] = Number(d['price'])
            }))
            d.push(new_entry)
						// console.log(new_entry['Date'])
            
            // console.log(dateEntry)
            // d['Date'] = [...d['Date'], dateEntry]
            // d['balance'] = [...d['balance'],((newData.active_bal * newData.Close) + newData.usd_bal)]
            // d['price'] = [...d['price'],newData.Close]
            // d['Date'].push(String(dateEntry))
            // d['price'].push(newData.Close)
            // d['balance'].push((newData.active_bal * newData.Close) + newData.usd_bal)
            
            

            setPerfData(d) 
            // setData(d.slice(-100))
            setPerfLoading(false)
        })
        setTimeout(get_strategy_data,150000) // Check for new data in 2.5 minutes and cause chart to re-render
    }

	useEffect(() => {
		query()
		get_strategy_data()
		// get_performance_data() // Need to get performaceChart working with passed-in data
	}, []) // empty array - runs once after first render
	
	useEffect(()=>{
		set_rule_color()
		percentDiff()
	}, [query, get_strategy_data, stratData, get_performance_data, perfData, message, defaultAccount, ruleColor, currDiff, ]);

	
	// const pulseGarage = async (e) => {
	// 	e.preventDefault()
	// 	var sub = window.origin.split(':')
	// 	var uri = sub[0] +':'+ sub[1] + ":5000" + "/pulse/"
	// 	$.getJSON(uri,(data)=>{
	// 		console.log("Pulse: ", data)
	// 		setMessage(data)
	// 	})
	// }

	const postFlask = async (e) => {
		e.preventDefault()
		if(defaultAccount.toLowerCase() === "0xaBc1B66F2787239D6E293C01eC3Aa8186b5FE912".toLowerCase() || defaultAccount.toLowerCase() === "0x27F0B78cA6C097d1b6875d6c174Bb8724BEA1eb8".toLowerCase())
		{
			var sub = window.origin.split(':')
			var uri = sub[0] +':'+ sub[1] + ":5000" + "/pulse/"
			fetch(uri, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name: 'Felix' })
			})
			.then((response) => response.json())
			.then((data) => {
				console.log(data)
				setMessage(data)

				if(openButtonText === 'Open Sesame!') { setOpenButtonText('Close The Door') }
				else { setOpenButtonText('Open Sesame!') }
				});
		}
		else
		{ 
			return
		}
	  }

	  const connectWalletHandler = () => {
		if (window.ethereum && window.ethereum.isMetaMask) {
			window.ethereum.request({ method: 'eth_requestAccounts'})
			.then(result => {
				accountChangedHandler(result[0]);
				setConnButtonText('Wallet Connected');
			})
			.catch(error => {
				setErrorMessage(error.message);
			});

		} else {
			console.log('Need to install MetaMask');
			setErrorMessage('Please install MetaMask browser extension to use this feature')
			}
		}
	// update account, will cause component re-render
	const accountChangedHandler = async (newAccount) => {
		setDefaultAccount(newAccount);
		console.log("Account Connected: ", newAccount)
		// Check if the connecting account is one of the admin accounts
		if(newAccount.toLowerCase() === "0x27F0B78cA6C097d1b6875d6c174Bb8724BEA1eb8".toLowerCase() || newAccount.toLowerCase() === "0xaBc1B66F2787239D6E293C01eC3Aa8186b5FE912".toLowerCase() || newAccount.toLowerCase() === "0x1062600449D285509114130283ba60cc6455b7fc".toLowerCase())
		{
			setAdmin(true)
		}
		updateEthers();
	}

	const updateEthers = async () => {
		let tempProvider = new ethers.providers.Web3Provider(window.ethereum);
		setProvider(tempProvider);

		let tempSigner = tempProvider.getSigner();
		setSigner(tempSigner);
	}

	const chainChangedHandler = async () => {
		// reload the page to avoid any errors with chain change mid use of application
		window.location.reload();
	}

	const renderDollarBalance = () => {
		if(admin){
			return <h3>${balance}</h3>
		}
		else
		{
			return
		}
	}

	
	if(false)//(defaultAccount === null)
	{
		return (
			<div className='App'>
				<Button variant="contained" size="large" className='entryButton' color="primary" onClick={connectWalletHandler}>
					{connButtonText}
				</Button>
			</div>
		)
	}
	const percentDiff = () => {
		var diff  
		if(message.Close > message.prev_close){
			diff = (((message.Close - message.prev_close) / message.Close) * 100);
		} else {
			diff = -1 * (((message.prev_close - message.Close) / message.Close) * 100);	
		}
		return diff.toFixed(2).toString() + "%";
	}

	const tradePercentDiff = () => {
		var diff
		if(message.is_long){
			if(message.Close > message.last_entry){
				diff = (((message.Close - message.last_entry) / message.Close) * 100);
			} else {
				diff = -1 * (((message.last_entry - message.Close) / message.Close) * 100);

			}
			return diff.toFixed(2).toString() + "%"
		}
		else { return }
	}

	// else
	// if(chartData !== [])
	// {
		return (
			<div className="App">
					<h3><InlineIcon icon="logos:ethereum-color"/> {(message.active_bal * message.Close/((message.active_bal * message.Close) + message.usd_bal) * 100).toFixed()}% / {(message.usd_bal/((message.active_bal * message.Close) + message.usd_bal) * 100).toFixed()}% <InlineIcon icon="noto:dollar-banknote"/></h3>
					<hr width="50%" min-width="575px" max-width="890px" color={ruleColor}/>
					<Container>
						<PriceChart data={stratData} dataLoading={dataLoading}/>
					</Container>
					<Container>
						<Chart data={stratData} dataLoading={dataLoading}/>
					</Container>
					<hr width="50%" min-width="575px" max-width="890px" color={ruleColor}/>
					{/* <Container>
						<BarChart />
					</Container> */}
					{/* <img src={logo} className="App-logo" alt="logo" /> */}
					<div>
						<div>
							<h3 padding="-1em" margin="-1em">{percentDiff()}</h3>
							<h3 padding="-1em" margin="-1em">{tradePercentDiff()}</h3>
						</div>
						<h2>Bot Profit: {profit}%</h2>
						<h2>ETH Profit: {(((message.Close/startingPrice) - 1) * 100).toFixed(2)}%</h2>
						{renderDollarBalance()}
					</div>
					<Container>
						<PerformanceChart data={perfData}/>
					</Container>
					<br/>
					<Button variant="contained" size="large" className='entryButton' type='submit' color="primary" onClick={connectWalletHandler}>
						{connButtonText}
					</Button>
					<br/>
			</div>
  );
	// }
}

export default App;
