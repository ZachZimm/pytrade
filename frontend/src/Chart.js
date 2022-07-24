import {csv, timeFormat} from "d3"
import React, {Component, useEffect, useState,} from 'react';
import useMeasure from 'react-use-measure'
import {defaultStyles, useTooltip, TooltipWithBounds} from "@visx/tooltip"
import {scaleLinear, scaleTime} from "@visx/scale"
import {Threshold} from "@visx/threshold"
import {extent, bisector} from "d3-array"
import { Group } from "@visx/group";
import { Line, LinePath, Bar } from "@visx/shape";
import { curveMonotoneX, curveCardinal, curveCardinalClosed, curveNatural, curveBasis } from "@visx/curve";
import { localPoint } from "@visx/event"
import styled from "styled-components";

const get_dev_sma = (d) => d['dev_sma'];
const get_dev_s_sma = (d) => d['dev_s_sma'];
const get_dev_s_s_sma = (d) => d['dev_s_s_sma'];
const get_dev_dir = (d) => d['dev_dir'];
const get_dev_upper = (d) => d['dev_upper']
const get_dev_lower = (d) => d['dev_lower']
const get_close = (d) => d['Close']
const get_open_long = (d) => d['open_long']
const get_close_long = (d) => d['close_long']
const getXValue = (d) => { return new Date(d['Date']) }
 
const bisectDate = bisector(getXValue).left;

const Wrapper = styled.div`
  
`;

const tooltipStyles = {
    ...defaultStyles,
    borderRadius: 4,
    background: "#1976d2",
    color: "white",
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
  };


const Chart = (props) => {
    const [loading, setLoading] = useState(true)
    const [data, setData] = useState([])
    const [dataCount, setDataCount] = useState(100)
    const [ref, bounds] = useMeasure()
    // const [ref2, bounds] = useMeasure()
    const {showTooltip, hideTooltip,tooltipData,tooltipLeft,tooltipTop} =  useTooltip();

    // const width = bounds.width || 100;
    // const height = bounds.height || 100;
    const width = 900
    const height = 400

    // const get_strategy_data = async () =>{
    //     csv('http://localhost:8080/strategy_data').then( (d) => {
    //         d.map((d) => {
    //             if(d['dev_sma'] === ""){ d['dev_sma'] = 0}
    //             if(d['dev_sma'] === "NaN"){ d['dev_sma'] = 0}
    //             if(d['dev_dir'] === ""){ d['dev_dir'] = 0}
    //             if(d['d'] === ""){ d['d'] = 0}
    //             let new_date = d['Date'].split('.')[0]
    //             d['Date'] = new_date
    //             d['dev_sma'] = Number(d['dev_sma'])
    //             d['d'] = Number(d['dev_dir'])
    //             d['dev_dir'] = Number(d['dev_dir'])
    //             d['dev_upper'] = Number(d['dev_upper'])
    //             d['dev_lower'] = Number(d['dev_lower'])
    //             d['Close'] = Number(d['Close'])
    //             d['dev'] = Number(d['dev'])
    //             d['0'] = 0
    //             d['y'] = d['Close']
    //         })
    //         // setData(d) 
    //         setData(d.slice(-1 * dataCount))
    //         setLoading(false)
    //         setTimeout(get_strategy_data,150000) // Check for new data in 2.5 minutes and cause chart to re-render
    //     })
    // }

    useEffect(() => {
		// if(loading === true)
		// {
            setData(props.data)
            setLoading(props.loading)
            // setLoading(false)
			// get_strategy_data()
		// }
		// query()
	}, [props.data, props.loading]);

    if(loading) return <div><h2>Loading...</h2></div>

    const xScale = scaleTime({
        range: [0, width],
        domain: extent(data,getXValue)
    }, [data])

    const yScale = scaleLinear({
        range: [height, 0],
        domain: [
            Math.min(Math.min(...data.map(get_dev_dir))-.025 ,Math.min(...data.map(get_dev_s_sma))-0.025),
            Math.max(Math.max(Math.max(...data.map(get_dev_dir))+.025 ,Math.max(...data.map(get_dev_s_sma))+0.025),0.025)
        ],
    },[data])

    return (
        <Wrapper>
            <svg ref={ref} width="100%" height="100%" viewBox={`0 0 ${width} ${height}`}>
                <Group>
                    <Threshold
                        id={`${Math.random()}`}
                        data={data}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y0={(d) => yScale(get_dev_s_s_sma(d)) ?? 0}
                        y1={(d) => yScale(get_dev_s_sma(d)) ?? 0}
                        clipAboveTo={0}
                        clipBelowTo={height}
                        curve={curveBasis}
                        belowAreaProps={{
                        fill: '#8080A6',
                        fillOpacity: 0.5,
                        }}
                        aboveAreaProps={{
                        fill: '#357341',
                        fillOpacity: 0.5,
                        }}
                    />
                    <LinePath
                        data={data}
                        key={(d) => `bar-${getXValue(d)}`}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(get_dev_sma(d)) ?? 0}
                        stroke="#d4841b"
                        strokeWidth={1.3}
                        curve={curveNatural}

                    />
                    <LinePath
                        data={data}
                        key={(d) => `bar-${getXValue(d)}`}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(get_dev_s_sma(d)) ?? 0}
                        stroke="#EDD2AE"
                        strokeWidth={1}
                        curve={curveNatural}

                    />
                    <LinePath
                        data={data}
                        key={(d) => `bar-${getXValue(d)}`}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(get_dev_s_s_sma(d)) ?? 0}
                        stroke="springgreen"
                        strokeWidth={1}
                        curve={curveNatural}

                    />
                    {/* <LinePath
                        data={data}
                        key={(d) => `bar-${getXValue(d)}`}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(get_dev_upper(d)) ?? 0}
                        stroke="#EDD2AE"
                        strokeWidth={.75}
                        curve={curveNatural}

                    />
                    <LinePath
                        data={data}
                        key={(d) => `bar-${getXValue(d)}`}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(get_dev_lower(d)) ?? 0}
                        stroke="#EDD2AE"
                        strokeWidth={.75}
                        curve={curveNatural}

                    /> */}
                    <LinePath
                        data={data}
                        key={Math.random()}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(get_dev_dir(d)) ?? 0}
                        stroke="#6CB8F4"
                        strokeWidth={1.5}
                        curve={curveBasis}

                    />
                    <LinePath
                        data={data}
                        key={Math.random()}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(0)}
                        stroke="gray"
                        strokeWidth={1}
                        strokeDasharray="5, 5"
                        curve={curveNatural}

                    />
                    <Bar
                        width={width}
                        height={height}
                        fill="transparent"
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(get_dev_dir(d)) ?? 0}
                        onMouseMove={(event) => {
                            const {x} = localPoint(event) || { x: 0 }
                            const x0 = xScale.invert(x)
                            const index = bisectDate(data,x0,1)
                            const d0 = data[index - 1]
                            const d1 = data[index]
                            let d = d0;
                            if(d1 && getXValue(d1)) {
                                d =
                                x0.valueOf() - getXValue(d0).valueOf() > // This is what I was looking for in regard to scale
                                getXValue(d1).valueOf() - x0.valueOf()
                                    ? d1
                                    : d0;
                            }

                            showTooltip({
                                tooltipData: d,
                                tooltipLeft: x,
                                tooltipTop: yScale(get_dev_dir(d))
                            });
                        }}
                        onMouseLeave={() => hideTooltip()}
                    />
                </Group>
                
            {tooltipData ? (
            <Group>
                <Line
                from={{ x: tooltipLeft, y: 0 }}
                to={{ x: tooltipLeft, y: height }}
                stroke="#59588D"
                strokeWidth={1}
                pointerEvents="none"
                strokeDasharray="5, 5"
                />
                <circle
                cx={tooltipLeft}
                cy={tooltipTop}
                r={4.5}
                fill="#FFEDB7"
                fillOpacity={0.65}
                pointerEvents="none"
                />
                <circle
                cx={tooltipLeft}
                cy={tooltipTop}
                r={2}
                fill="#9FE37E"
                pointerEvents="none"
                />
            </Group>
            ) : null}
        </svg>

        {tooltipData ? (
        <TooltipWithBounds
          key={getXValue(tooltipData)}
          top={tooltipTop}
          left={tooltipLeft}
          style={tooltipStyles}
        >
          {`${timeFormat("%b %d %H:%M ")(new Date(getXValue(tooltipData)))}`}<br/>
          {/* <br/><b>{get_dev_dir(tooltipData).toFixed(2)}</b><br/> */}
          {/* <b>{get_dev_s_sma(tooltipData).toFixed(2)}</b><br/> */}
          Diff: <b>{((get_dev_s_s_sma(tooltipData)-get_dev_s_sma(tooltipData))*100).toFixed(2)}</b><br/>
        </TooltipWithBounds>
      ) : null}

    </Wrapper>
    );
};

export default Chart;
