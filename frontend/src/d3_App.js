import {useState, useEffect, useRef } from "react";
import * as d3 from "d3";

// const data = [
//   { name: "A", value: 100 },
//   { name: "B", value: 200 },
//   { name: "C", value: 500 },
//   { name: "D", value: 150 },
//   { name: "E", value: 300 },
// ];

const margin = { top: 30, right: 0, bottom: 30, left: 40 };

const height = 250;

const width = 300;

const App = () => {
  const ref = useRef();
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState([])

  const get_strategy_data = async () =>{
		d3.csv('http://71.94.94.154:8080/strategy_data').then( (d) => {
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
			setData(d)
			setLoading(false)
		})
	}
  useEffect(() => {
    if(loading === true)
		{
			get_strategy_data()
		}
  }, [])

  useEffect(() => {
    

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.dev_sma + 1)])
      .nice()
      .range([height - margin.bottom, margin.top]);

    const x = d3
      .scaleBand()
      .domain(d3.range(data.length))
      .range([margin.left, width - margin.right])
      .padding(0.1);

    const svg = d3
      .select(ref.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    const yAxis = (g) =>
      g
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y).ticks(null, data.format))
        .call((g) => g.select(".domain").remove())
        .call((g) =>
          g
            .append("text")
            .attr("x", -margin.left)
            .attr("y", 10)
            .attr("fill", "currentColor")
            .attr("text-anchor", "start")
            .text(data.y)
        );

    const xAxis = (g) =>
      g.attr("transform", `translate(0,${height - margin.bottom})`).call(
        d3
          .axisBottom(x)
          .tickFormat((i) => data[i].Date)
          .tickSizeOuter(0)
      );

    svg.append("g").call(xAxis);

    svg.append("g").call(yAxis);

    svg
      .append("g")
      .selectAll("rect")
      .data(data)
      .join(
        (enter) => enter.append("rect"),
        (update) => update,
        (exit) => exit.remove()
      )
      .attr("x", (d, i) => x(i))
      .attr("y", (d) => y(d.dev_sma))
      .attr("height", (d) => (1 + (y(0) - y(d.dev_sma))))
      .attr("width", x.bandwidth());
  }, [data, loading]);

  return <div ref={ref} />;
};

export default App;