import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import Card from "../components/Card";
import LoadingPage from "../components/Loading";

export default function PortfolioPage() {
  const router = useRouter();

  let [portfolioData, setPortfolioData] = useState(null);
  let [total, setTotal] = useState(null);

  useEffect(() => {
    fetch("/api/portfolio")
      .then((r) => r.json())
      .then((r) => {
        // TODO: only redirect unauthenticated user.
        if ("error" in r) {
          router.replace("/login");
        } else {
          r = r.map((data) => {
            let mv = data.last * data.volume;
            return { marketValue: mv, pl: mv - data.cost, ...data };
          });
          setTotal(r.reduce((sum, cur) => sum + cur.pl, 0));
          setPortfolioData(r);
        }
      });
  }, [router]);
  let table = (
    <div className="overflow-auto">
      <table>
        <thead>
          <tr className="border-b-2 border-b-gray-300">
            <th>Stock Name/Code</th>
            <th
              title=" Last Price / Average Price"
              className="hover:cursor-help"
            >
              <p>Last /</p>
              <p>Avg</p>
            </th>
            <th title="Market Value / Volume Bought" className="hover:cursor-help">
              <p >
                MV /
              </p>
              <p>Qty</p>
            </th>
            <th>Unrealized P/L</th>
          </tr>
        </thead>
        <tbody>
          {portfolioData == null ||
            portfolioData.map((data) => <Row key={data.code} data={data} />)}
          {total && (
            <tr>
              <td>Total</td>
              <td
                className={total > 0 ? "text-green-500" : "text-red-500"}
                colSpan={3}
              >
                {total.toFixed(2)}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
  let loadedPage =
    portfolioData == null || portfolioData.length === 0 ? (
      <Card>
        <p className="text-lg font-semibold text-center">
          No Transaction Found
        </p>
      </Card>
    ) : (
      table
    );
  return (
    <>
      <h1>Portfolio</h1>
      {portfolioData == null ? <LoadingPage /> : loadedPage}
    </>
  );
}

function Row({ data }) {
  let { code, name, avg_price: price, volume, last, marketValue, pl } = data;

  return (
    <tr className="odd:bg-gray-50 even:bg-white">
      <td>
        <p className="font-bold ">{name}</p>
        <p className="text-sm text-gray-700">{code}</p>
      </td>
      <td>
        <p>{last.toFixed(3)}</p>
        <p>{price.toFixed(3)}</p>
      </td>
      <td>
        <p>{marketValue.toFixed(2)}</p>
        <p>{volume}</p>
      </td>
      <td className={pl > 0 ? "text-green-500" : "text-red-500"}>
        {pl.toFixed(2)}
      </td>
    </tr>
  );
}
