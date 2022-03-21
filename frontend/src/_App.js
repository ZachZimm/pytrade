import logo from './logo.svg';
import './App.css';
import React, {useRef, useEffect, useState} from 'react';
import {ethers} from 'ethers'
import $, { data } from 'jquery'

import Button from '@mui/material/Button';
import { InlineIcon } from '@iconify/react';

import { letterFrequency } from '@visx/mock-data';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleLinear, scaleBand } from '@visx/scale';
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

import React from 'react';


// We'll use some mock data from `@visx/mock-data` for this.
// const data = letterFrequency;
// Define the graph dimensions and margins
const width = 500;
const height = 500;
const margin = { top: 20, bottom: 20, left: 20, right: 20 };
// Then we'll create some bounds
const xMax = width - margin.left - margin.right;
const yMax = height - margin.top - margin.bottom;
// We'll make some helpers to get at the data we want
const x = d => d.Date;
const y = d => +d.dev_sma
// And then scale the graph by our data
const xScale = scaleBand({
  range: [0, xMax],
  round: true,
  domain: chartData.map(x),
  padding: 0.4,
});
const yScale = scaleLinear({
  range: [yMax, 0],
  round: true,
  domain: [0, Math.max(...chartData.map(y))],
});
// Compose together the scale and accessor functions to get point functions
const compose = (scale, accessor) => data => scale(accessor(data));
const xPoint = compose(xScale, x);
const yPoint = compose(yScale, y);


const  App = () => {
	const [message, setMessage] = useState([{}])
	const [count, setCount] = useState(0)
	const [intervalStarted, setIntervalStarted] = useState(false)
	const [openButtonText, setOpenButtonText] = useState('Check Faster!')
	const [defaultAccount, setDefaultAccount] = useState(null);
	const [connButtonText, setConnButtonText] = useState('Connect Wallet');
	const [errorMessage, setErrorMessage] = useState(null);
	const [provider, setProvider] = useState(null);
	const [signer, setSigner] = useState(null);

	const [chartData, setChartData] = useState([])
	const [loading, setLoading] = useState(true)
	const [width,setWidth] = useState(0)
	const [height,setHeight] = useState(0)
	const [margin,setMargin] = useState(0)
	const [xMax,setXMax] = useState(0)
	const [yMax,setYMax] = useState(0)
	const [x,setX] = useState(0)
	const [y,setY] = useState(0)
	const [xScale,setXScale] = useState({})
	const [yScale,setYScale] = useState({})
	const [xPoint,setXPoint] = useState({})
	const [yPoint,setYPoint] = useState({})
	const svgRef = useRef();

	const [mockData, setMockData] = useState([25,30,45,60,20,65,76]);

	// Check this out: https://codesandbox.io/s/with-time-scale-x-axis-y5pt3?from-embed=&file=/src/App.js:1226-1231

	$.ajaxSetup({
		crossDomain: true
	})
	const query = async () => {
		var request = '/data' // This should be passed in as an arg
		var sub = window.origin.split(':')
		var uri = sub[0] +':'+ sub[1]
		uri = uri + ':8080' + request
		// console.log(origin)
		
		$.getJSON(uri, function(data){
			console.log("Response: ", data)
			setMessage(data)
		})
		// setPrice(price + 1)
		setTimeout(query,5000)
	}

	const get_close = (val) => val
	const get_date = (val) => {
		let form =  timeFormat("%Y-%m-%d %H:%M:%S")
		return form(val)
	}
	const compose = (scale, accessor) => data => scale(accessor(data));

	const get_strategy_data = async () =>{
		csv('http://71.94.94.154:8080/strategy_data').then( (d) => {
			// console.log(d.Date)
			d.map((d) => {
				// let formatted_date = get_date(d['Date'].split('.')[0])
				if(d['dev_sma'] === ""){ d['dev_sma'] = 0}
				if(d['dev_dir'] === ""){ d['dev_dir'] = 0}
				if(d['d'] === ""){ d['d'] = 0}
				let new_date = d['Date'].split('.')[0]
				d['Date'] = new_date
				d['dev_sma'] = Number(d['dev_sma'])
				d['d'] = Number(d['dev_dir'])
				d['dev_dir'] = Number(d['dev_dir'])
				d['Close'] = Number(d['Close'])
				d['dev'] = Number(d['dev'])
				d['0'] = 0
				// setChartData({"date":formatted_date, "dev_sma": d['dev_sma'], "dev_dir": d['dev_dir']})
				// console.log(chartData)
				// console.log("Loaded Data: ")
				// console.log(chartData)

			})
			console.log(d)
			setChartData(d)
			setLoading(false)
		})
	}
	useEffect(() => {
		if(loading === true)
		{
			get_strategy_data()
		}
		// console.log("1")
		query()
	}, []) // empty array - runs once after first render
	
	useEffect(()=>{
		// if(loading === false)
		// {
			console.log("chartData:")
			console.log(chartData)
			const svg = select(svgRef.current);
			const myLine = line()
				.x((value,index) => index * 2)
				.y(value => 150 - value)
				.curve(curveCardinal);

			svg.selectAll("path").data([mockData]).join("path")
				.attr("class", "path")
				.attr("d", value => myLine(value).path)
				// .attr("x",value => value['Date'])
				.attr("fill","none")
				.attr("stroke", "blue")
				.attr("width", "100%")
				.attr("height", "100%");
		// }
			


		// setWidth(500)
		// setHeight(500)
		// setMargin({ top: 20, bottom: 20, left: 20, right: 20 })
		// // Then we'll create some bounds
		// setXMax(width - margin.left - margin.right)
		// setYMax(height - margin.top - margin.bottom)
		// // We'll make some helpers to get at the data we want
		// setX(chartData => chartData.Date)
		// setY(chartData => +chartData.dev_sma)
		// // And then scale the graph by our data
		// setXScale(scaleBand({
		// 	range: [0, xMax],
		// 	round: true,
		// 	domain: chartData.map(Date),
		// 	padding: 0.4,
		// }))
		// setYScale(scaleLinear({
		// 	range: [yMax, 0],
		// 	round: true,
		// 	domain: [0, Math.max(...chartData.map(dev_dir))],
		// }))
		// // Compose together the scale and accessor functions to get point functions
		// setXPoint(compose(xScale, x))
		// setYPoint(compose(yScale, y))


	}, [chartData, loading, query]);

	

	

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

				<svg width={width} height={height}>
					{chartData.map((dev_sma, Date) => {
						const barHeight = yMax - yPoint(dev_sma);
						return (
						<Group key={`bar-${Date}`}>
							<Bar
							x={xPoint(dev_sma)}
							y={yMax - barHeight}
							height={barHeight}
							width={xScale.bandwidth()}
							fill="#fc2e1c"
							/>
						</Group>
						);
					})}
				</svg>
				{/* <svg ref={svgRef}></svg> */}
				{/* <img src={logo} className="App-logo" alt="logo" /> */}
				<h2>AVAX: ${message.Close}</h2>  
				<h2>Pytrade Bot Balance: ${((message.avax_bal * message.Close) + message.usd_bal).toFixed(2)}</h2>
				
				<h3><InlineIcon icon="logos:ethereum-color"/> {(message.avax_bal * message.Close/((message.avax_bal * message.Close) + message.usd_bal) * 100).toFixed()}% / {(message.usd_bal/((message.avax_bal * message.Close) + message.usd_bal) * 100).toFixed()}% <InlineIcon icon="noto:dollar-banknote"/></h3>
				<Button variant="contained" size="large" className='entryButton' type='submit' color="primary" onClick={query}>
					{openButtonText}
				</Button>

			</div>
  );
	// }
}

export default App;
