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
	width: 900px;
	height: 400px;
	border-radius: 40px;
	position: relative;
	overflow: hidden
`;
// min-width: 300px;
// background-color: #201d47; - purplish

const  App = () => {
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

	const startingBal = 500
	const startingPrice = 83.8

	$.ajaxSetup({
		crossDomain: true
	})
	const query = async () => {
		var request = '/data' // This should be passed in as an arg
		// var sub = window.origin.split(':') // For use when frontend, backend, and client are on the same network, sometimes
		// var uri = sub[0] +':'+ sub[1]

		// Maybe do if(origin == localhost) {}
		var uri = 'http://71.94.94.154:8080' + request
		// console.log(origin)
		
		$.getJSON(uri, function(data){
			console.log("Response: ", data)
			setBalance(((data.avax_bal * data.Close) + data.usd_bal).toFixed(2))
			setProfit((((((data.avax_bal * data.Close) + data.usd_bal)/startingBal)-1)*100).toFixed(2)) // This uses a hard-coded starting value
			setMessage(data)
		})
		// setPrice(price + 1)
		
		setTimeout(query,5000)
	}

	useEffect(() => {
		query()
	}, []) // empty array - runs once after first render
	
	useEffect(()=>{

	}, [query, defaultAccount]);

	
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
			setErrorMessage('Please install MetaMask browser extension to interact');
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

	// const interval = setInterval(async () => {
	// 	// method to be executed;
	// 	setCount(count + 1)
	// 	console.log(count)
	// 	// setIntervalStarted(true)
	//   }, 5000);

	// listen for account changes
	// window.ethereum.on('accountsChanged', accountChangedHandler);

	// window.ethereum.on('chainChanged', chainChangedHandler);
	// {chart_data.map((Date, dev_sma) => {
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
	// else
	// if(chartData !== [])
	// {
		return (
			<div className="App">
					<h3><InlineIcon icon="logos:ethereum-color"/> {(message.avax_bal * message.Close/((message.avax_bal * message.Close) + message.usd_bal) * 100).toFixed()}% / {(message.usd_bal/((message.avax_bal * message.Close) + message.usd_bal) * 100).toFixed()}% <InlineIcon icon="noto:dollar-banknote"/></h3>
					<Container>
						<PriceChart />
					</Container>
					<Container>
						<Chart />
					</Container>
					{/* <Container>
						<BarChart />
					</Container> */}
					{/* <img src={logo} className="App-logo" alt="logo" /> */}
					<div>
						<h2>Bot Profit: {profit}%</h2>
						<h2>AVAX Profit: {(((message.Close/startingPrice) - 1) * 100).toFixed(2)}%</h2>
						{renderDollarBalance()}
					</div>
					<Container>
						<PerformanceChart />
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
