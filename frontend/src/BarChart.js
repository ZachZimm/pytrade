import { useMemo, useState, TouchEvent, MouseEvent, useEffect } from "react";
import { Bar } from "@visx/shape";
import appleStock, { AppleStock } from "@visx/mock-data/lib/mocks/appleStock";
import { scaleBand, scaleLinear } from "@visx/scale";
import { localPoint } from "@visx/event";
import { TooltipWithBounds, useTooltip, defaultStyles } from "@visx/tooltip";
import { Axis, AxisBottom, AxisLeft } from "@visx/axis";
import {
  AnimatedAxis, // any of these can be non-animated equivalents
  AnimatedGrid,
  AnimatedLineSeries,
  XYChart,
  Tooltip,
} from '@visx/xychart';
import useMeasure from "react-use-measure";
import styled from "styled-components";
import { timeFormat } from "d3-time-format";
import { Group } from "@visx/group";
import {csv} from "d3"

// const data = appleStock.slice(0, 10);

const getYValue = (d) => d['dev_sma'];
const getYValue2 = (d) => d['dev_dir'];

const getXValue = (d) => d['Date'];

const Wrapper = styled.div`
  
`;
// wrapper:
// width: 100%;
//   height: 100%;
//   display: flex;
//   align-items: center;
//   justify-content: center;


const tooltipStyles = {
  ...defaultStyles,
  borderRadius: 4,
  background: "#1976d2",
  color: "white",
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
};

const tickLabelProps = () => ({
  fill: "none",
  fontSize: 4,
  fontFamily: "sans-serif",
  // textAnchor: "tight"
});

const margin = 16;

const Chart = () => {
  const [ref, bounds] = useMeasure();
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState([])

  const width = bounds.width || 100;
  const height = bounds.height || 100;

  const innerWidth = width - margin;
  const innerHeight = height - margin;

  const get_strategy_data = async () =>{
		csv('http://71.94.94.154:8080/strategy_data').then( (d) => {
			// console.log(d.Date)
			d.map((d) => {
				// let formatted_date = get_date(d['Date'].split('.')[0])
				if(d['dev_sma'] === ""){ d['dev_sma'] = 0}
        if(d['dev_sma'] === "NaN"){ d['dev_sma'] = 0}
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
        d['y'] = d['Close']
				// setChartData({"date":formatted_date, "dev_sma": d['dev_sma'], "dev_dir": d['dev_dir']})
				// console.log(chartData)
				// console.log("Loaded Data: ")
				// console.log(chartData)

			})
			// console.log(d)
			// setData(d) 
      setData(d.slice(d.length-101, d.length-1))
			setLoading(false)
		})
	}

  // useEffect(() => {
  const {
    showTooltip,
    hideTooltip,
    tooltipData,
    tooltipLeft = 0,
    tooltipTop = 0,
  } = useTooltip();

  const xScale = useMemo(
    () =>
      scaleBand({
        range: [margin, innerWidth],
        domain: data.map(getXValue),
        padding: 0.2,
      }),
    [innerWidth, data]
  );

  const yScale = useMemo(
    () =>
      scaleLinear({
        range: [innerHeight, margin],
        domain: [
          Math.min(...data.map(getYValue2)) - 1,
          Math.max(...data.map(getYValue2)) + 1,
        ],
      }),
    [innerHeight, data]
  );
  // }, [data, loading])

  useEffect(() => {
		if(loading === true)
		{
			get_strategy_data()
		}
		// console.log(data)
		// query()
	}, [data]) // empty array - runs once after first render

  if(data.length !== 0)
  {
    return (
      <Wrapper>
          <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`}>
            <Group>
              {data.map((d) => {
                const xValue = getXValue(d);
                const barWidth = xScale.bandwidth();
                const barHeight = innerHeight - (yScale(getYValue(d)) ?? 0);
                const barHeight2 = innerHeight - (yScale(getYValue2(d)) ?? 0);
                const barX = xScale(xValue);
                const barY = innerHeight - barHeight;
                const barY2 = innerHeight - barHeight2;
  
                return (
                  <Group>
                    <Bar
                      key={Math.random()} // Not sure why exactaly I need the key here
                      x={barX}
                      y={barY}
                      width={barWidth}
                      height={barHeight}
                      fill="#61dafb"
                      onMouseMove={(event) => {
                        const point = localPoint(event);
    
                        if (!point) return;
    
                        showTooltip({
                          tooltipData: d,
                          tooltipTop: point.y,
                          tooltipLeft: point.x,
                        });
                      }}
                      onMouseLeave={() => hideTooltip()}
                    />
                    <Bar
                      key={`bar-${xValue}`}
                      x={barX}
                      y={barY2}
                      width={barWidth}
                      height={barHeight}
                      fill="#ff8e14"
                      onMouseMove={(event) => {
                        const point = localPoint(event);
    
                        if (!point) return;
    
                        showTooltip({
                          tooltipData: d,
                          tooltipTop: point.y,
                          tooltipLeft: point.x,
                        });
                      }}
                      onMouseLeave={() => hideTooltip()}
                    />
                  </Group>
                );
              })}
            </Group>
            
  
            {/* <Group>
              <AxisBottom
                top={innerHeight}
                scale={xScale}
                tickFormat={(date) => timeFormat("%H:%M")(new Date(date))}
              />
            </Group> */}
  
            <Group>
              <AxisLeft 
              left={margin} 
              scale={yScale} 
              stroke='none'
              tickStroke="none"
              tickLabelProps={tickLabelProps}
              />
            </Group>
            
          </svg>
  
          {tooltipData ? (
            <TooltipWithBounds
              key={Math.random()}
              top={tooltipTop}
              left={tooltipLeft}
              style={tooltipStyles}
            >
              <b>{`${timeFormat("%b %d, %Y")(
                new Date(getXValue(tooltipData))
              )}`}</b>
              : ${getYValue(tooltipData).toFixed(3)}
            </TooltipWithBounds>
          ) : null}
      </Wrapper>
    );
  }
  else
  {
    return(
      <div>
        <h2>Data Not Loaded</h2>
      </div>
    )
  }
  }

export default Chart;