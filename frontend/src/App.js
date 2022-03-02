import logo from './logo.svg';
import './App.css';
import React, {useEffect, useState} from 'react';
import {ethers} from 'ethers'
import $, { data } from 'jquery'

import Button from '@mui/material/Button';
// import TextField from "@material-ui/core/TextField";
// import { makeStyles } from "@material-ui/core/styles";
// import { FormControl, FormControlLabel, FormLabel, Radio, RadioGroup } from '@material-ui/core';

// const useStyles = makeStyles((theme) => ({
// 	root: {
// 	  "& > *": {
// 		margin: theme.spacing(1),
// 	  },
// 	},
//    }));

function App() {
	const [message, setMessage] = useState({})
	const [openButtonText, setOpenButtonText] = useState('Open Sesame!')
	const [defaultAccount, setDefaultAccount] = useState(null);
	const [connButtonText, setConnButtonText] = useState('Connect Wallet');
	const [errorMessage, setErrorMessage] = useState(null);
	const [provider, setProvider] = useState(null);
	const [signer, setSigner] = useState(null);

	$.ajaxSetup({
		crossDomain: true
	})
	const query = async () => {
		var request = '/api/1' // This should be passed in as an arg
		var sub = window.origin.split(':')
		var uri = sub[0] +':'+ sub[1]
		uri = uri + ':5000' + request
		console.log(uri)
		
		$.getJSON(uri, function(data){
			console.log("Response: ", data)
			setMessage(data)
		})
	}
	
	useEffect(()=>{
		query()
	}, [])

	const pulseGarage = async (e) => {
		e.preventDefault()
		var sub = window.origin.split(':')
		var uri = sub[0] +':'+ sub[1] + ":5000" + "/pulse/"
		$.getJSON(uri,(data)=>{
			console.log("Pulse: ", data)
			setMessage(data)
		})
		console.log(uri)
	}

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

	// listen for account changes
	window.ethereum.on('accountsChanged', accountChangedHandler);

	window.ethereum.on('chainChanged', chainChangedHandler);
	
	if(defaultAccount === null)
	{
		return (
			<div className='App'>
				<Button variant="contained" size="large" className='entryButton' color="primary" onClick={connectWalletHandler}>
					{connButtonText}
				</Button>
			</div>
		)
	}
	else
	{
		return (
			<div className="App">
				<header className="App-header">
					<img src={logo} className="App-logo" alt="logo" />
					<p>
						Blockhain-Authenticated Garage Door
					</p>
					<h3>{message.name}</h3> 
					{/* <form onSubmit={postFlask}> */}
					<Button variant="contained" size="large" className='entryButton' type='submit' color="primary" onClick={postFlask}>
						{openButtonText}
					</Button>
					{/* </form> */}
				</header>
			</div>
  );
	}
}

export default App;
