import {csv, timeFormat} from "d3"
import React, {useEffect, useState,} from 'react';
import useMeasure from 'react-use-measure'
import {defaultStyles, useTooltip, TooltipWithBounds} from "@visx/tooltip"
import {scaleLinear, scaleTime} from "@visx/scale"
import {extent, bisector} from "d3-array"
import { Group } from "@visx/group";
import { Line, LinePath, Bar } from "@visx/shape";
import { curveMonotoneX, curveCardinal, curveCardinalClosed, curveNatural, curveBasis } from "@visx/curve";
import { localPoint } from "@visx/event"
import { Axis, AxisBottom, AxisLeft } from "@visx/axis";

const tickLabelProps = () => ({
    fill: "#a6a6a6",
    fontSize: 11,
    fontFamily: "sans-serif",
    label: "%"
  });

const getYValue = (d) => (d['price']/83.8);
const getYValue2 = (d) => (d['balance']/500);

const getXValue = (d) => { return new Date(d['Date']) }
 
const bisectDate = bisector(getXValue).left;


const tooltipStyles = {
    ...defaultStyles,
    borderRadius: 4,
    background: "#1976d2",
    color: "white",
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
  };

  const accessors = {
    xAccessor: d => d['Date'],
    yAccessor: d => d['price'],
  };


const PerformanceChart = () => {
    const [loading, setLoading] = useState(true)
    const [data, setData] = useState([])
    const [ref, bounds] = useMeasure()
    const {showTooltip, hideTooltip,tooltipData,tooltipLeft,tooltipTop} =  useTooltip();

    const width = bounds.width || 100;
    const height = bounds.height || 100;

    const get_strategy_data = async () =>{
        csv('http://71.94.94.154:8080/strategy_log').then( (d) => {
            d.map((d) => {
                let new_date = d['Date'].split('.')[0]
                d['Date'] = new_date
                d['price'] = Number(d['price'])
            })
            setData(d) 
            // setData(d.slice(-100))
            setLoading(false)
            setTimeout(get_strategy_data,150000) // Check for new data in 2.5 minutes and cause chart to re-render
        })
    }

    useEffect(() => {
		if(loading === true)
		{
			get_strategy_data()
		}
		console.log(data)
		// query()
	}, [data]);

    if(loading) return <div><h2>Loading...</h2></div>

    const xScale = scaleTime({
        range: [0, width],
        domain: extent(data,getXValue)
    }, [data])

    const yScale = scaleLinear({
        range: [height, 0],
        domain: [
            Math.min(...data.map(getYValue2))- 0.1,
            Math.max(...data.map(getYValue2)) + 0.2,
        ],
    },[data])

    return (<>
            <svg ref={ref} width="100%" height="100%" viewBox={`0 0 ${width} ${height}`}>
                <Group>
                    <LinePath
                        data={data}
                        key={(d) => `bar-${getXValue(d)}`}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(getYValue(d)) ?? 0}
                        stroke="#F5D482"
                        strokeWidth={2}
                        curve={curveMonotoneX}

                    />
                    <LinePath
                        data={data}
                        key={Math.random()}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(getYValue2(d)) ?? 0}
                        stroke="#6CB8F4"
                        strokeWidth={2}
                        curve={curveMonotoneX}

                    />
                    <LinePath
                        data={data}
                        key={Math.random()}
                        x={(d) => xScale(getXValue(d)) ?? 0}
                        y={(d) => yScale(1)}
                        stroke="gray"
                        strokeWidth={1}
                        strokeDasharray="5, 5"
                        curve={curveMonotoneX}

                    />
                </Group>
                <Group>
                    <AxisLeft 
                        left={0} 
                        scale={yScale} 
                        stroke='none'
                        tickStroke="none"
                        tickLabelProps={tickLabelProps}
                        numTicks={5}
                    />
                </Group>
                {tooltipData ? (
                    <Group>
                        <Bar
                            key={Math.random()}
                            width={width}
                            height={height}
                            fill="transparent"
                            x={(d) => xScale(getXValue(d)) ?? 0}
                            y={(d) => yScale(getYValue2(d)) ?? 0}
                            onMouseMove={(event) => {
                                const {x} = localPoint(event) || { x: 0 }
                                const x0 = xScale.invert(x)
                                const index = bisectDate(data,x0,1)
                                const d0 = data[index - 1]
                                const d1 = data[index]
                                let d = d0;
                                if(d1 && getXValue(d1)) {
                                    d =
                                    x0.valueOf() - getXValue(d0).valueOf() >
                                    getXValue(d1).valueOf() - x0.valueOf()
                                        ? d1
                                        : d0;
                                }

                                showTooltip({
                                    tooltipData: d,
                                    tooltipLeft: x,
                                    tooltipTop: yScale(getYValue2(d))
                                });
                            }}
                            onMouseLeave={() => hideTooltip()}
                        />
                    </Group>
                ): null }
                
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
                r={8}
                fill="#FF4DCA"
                fillOpacity={0.5}
                pointerEvents="none"
                />
                <circle
                cx={tooltipLeft}
                cy={tooltipTop}
                r={4}
                fill="#FF4DCA"
                pointerEvents="none"
                />
            </Group>
            ) : null}
        </svg>
        {tooltipData ? (
        <TooltipWithBounds
          key={Math.random()}
          top={tooltipTop}
          left={tooltipLeft}
          style={tooltipStyles}
        >
          {`${timeFormat("%b %d %H:%M ")(new Date(getXValue(tooltipData)))}`}:{" "}
          <b>{getYValue2(tooltipData)}</b>
        </TooltipWithBounds>
      ) : null}
        </>
    );
};

export default PerformanceChart;