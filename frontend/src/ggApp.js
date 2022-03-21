import React, { useState, useMemo } from "react";
import AreaClosed from "@visx/shape/lib/shapes/AreaClosed";
import { curveMonotoneX } from "@visx/curve";
import {
  scaleUtc,
  scaleLinear,
  scaleLog,
  scaleBand,
  coerceNumber
} from "@visx/scale";
import { Orientation } from "@visx/axis";
import {
  AnimatedAxis,
  AnimatedGridRows,
  AnimatedGridColumns
} from "@visx/react-spring";
import { LinearGradient } from "@visx/gradient";
import { timeFormat } from "d3-time-format";
  
export const backgroundColor = "#da7cff";
const axisColor = "#fff";
const tickLabelColor = "#fff";
export const labelColor = "#340098";
const gridColor = "#6e0fca";
const margin = {
  top: 40,
  right: 150,
  bottom: 20,
  left: 50
};
  
const tickLabelProps = () => ({
  fill: tickLabelColor,
  fontSize: 12,
  fontFamily: "sans-serif",
  textAnchor: "middle"
});
  
const getMinMax = (vals) => {
  const numericVals = vals.map(coerceNumber);
  return [Math.min(...numericVals),
          Math.max(...numericVals)];
};
  
function Chart({
  width: outerWidth = 800,
  height: outerHeight = 800,
  showControls = true
}) {
  const width = outerWidth - margin.left - margin.right;
  const height = outerHeight - margin.top - margin.bottom;
  const [dataToggle] = useState(true);
  const [animationTrajectory] = useState("center");
  
  const axes = useMemo(() => {
    const linearValues = dataToggle ? [0, 2, 4, 6, 8, 10] :
                                      [6, 8, 10, 12];
  
  return [
      {
        scale: scaleLinear({
          domain: getMinMax(linearValues),
          range: [0, width]
        }),
        values: linearValues, // Change this to data['dev_sma']
        tickFormat: (v, index, ticks) =>
          index === 0
            ? "first"
            : index === ticks[ticks.length - 1].index
            ? "last"
            : `${v}`,
        label: "linear"
      }
    ];
  }, [dataToggle, width]);
  
  if (width < 10) return null;
  
  const scalePadding = 40;
  const scaleHeight = height / axes.length - scalePadding;
  
  const yScale = scaleLinear({
    domain: [100, 0],
    range: [scaleHeight, 0]
  });
  
  return (
    <>
      <svg width={outerWidth} height={outerHeight}>
        <LinearGradient
          id="visx-axis-gradient"
          from={backgroundColor}
          to={backgroundColor}
          toOpacity={0.5}
        />
        <rect
          x={0}
          y={0}
          width={outerWidth}
          height={outerHeight}
          fill={"url(#visx-axis-gradient)"}
          rx={14}
        />
        <g transform={`translate(${margin.left},${margin.top})`}>
          {axes.map(({ scale, values, label, tickFormat }, i) => (
            <g
              key={`scale-${i}`}
              transform={`translate(0, ${i * (scaleHeight + scalePadding)})`}
            >
              <AnimatedGridRows
                key={`gridrows-${animationTrajectory}`}
                scale={yScale}
                stroke={gridColor}
                width={width}
                numTicks={dataToggle ? 1 : 3}
                animationTrajectory={animationTrajectory}
              />
              <AnimatedGridColumns
                key={`gridcolumns-${animationTrajectory}`}
                scale={scale}
                stroke={gridColor}
                height={scaleHeight}
                numTicks={dataToggle ? 5 : 2}
                animationTrajectory={animationTrajectory}
              />
              <AreaClosed
                data={values.map((x) => [
                  (scale(x) ?? 0) +
                    ("bandwidth" in scale &&
                    typeof scale.bandwidth !== "undefined"
                      ? scale.bandwidth() / 2
                      : 0),
                  yScale(10 + Math.random() * 90)
                ])}
                yScale={yScale}
                curve={curveMonotoneX}
                fill={gridColor}
                fillOpacity={0.2}
              />
              <AnimatedAxis
                key={`axis-${animationTrajectory}`}
                orientation={Orientation.bottom}
                top={scaleHeight}
                scale={scale}
                tickFormat={tickFormat}
                stroke={axisColor}
                tickStroke={axisColor}
                tickLabelProps={tickLabelProps}
                tickValues={
                  label === "log" || label === "time" ? undefined : values
                }
                numTicks={label === "time" ? 6 : undefined}
                label={label}
                labelProps={{
                  x: width + 30,
                  y: -10,
                  fill: labelColor,
                  fontSize: 18,
                  strokeWidth: 0,
                  stroke: "#fff",
                  paintOrder: "stroke",
                  fontFamily: "sans-serif",
                  textAnchor: "start"
                }}
                animationTrajectory={animationTrajectory}
              />
            </g>
          ))}
        </g>
      </svg>
    </>
  );
}
  
export default function App() {
  return (
    <div>
      <Chart width="500" height="300" />
    </div>
  );
}