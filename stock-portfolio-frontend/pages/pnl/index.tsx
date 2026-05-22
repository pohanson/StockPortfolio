import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import Card from "../../components/Card";
import LoadingPage from "../../components/Loading";

type PNLReportLineItem = {
  code: string;
  name: string;
  dividend_earnings: number;
  transaction_earnings: number;
};
export default function NetPage() {
  const router = useRouter();

  const [pnlData, setPnlData] = useState<null | PNLReportLineItem[]>(null);

  useEffect(() => {
    fetch("/api/pnl")
      .then((r) => {
        if (r.status === 401) {
          router.replace("/login");
        } else {
          return r.json();
        }
      })
      .then((json) => {
        setPnlData(json);
      });
  }, [router]);
  let totalEarnings: number | null = null,
    totalDividend: number | null = null,
    totalTransaction: number | null = null;
  if (pnlData != null) {
    totalTransaction = pnlData.reduce(
      (sum, cur) => sum + cur.transaction_earnings,
      0,
    );
    totalDividend = pnlData.reduce(
      (sum, cur) => sum + cur.dividend_earnings,
      0,
    );
    totalEarnings = totalTransaction + totalDividend;
  }

  let table = (
    <table className="overflow-auto md:overflow-y-visible md:mb-4">
      <thead>
        <tr className="border-b-2 border-b-gray-300">
          <th>Stock Name/Code</th>
          <th>Transactions</th>
          <th>Dividend</th>
          <th>Total Earnings</th>
        </tr>
      </thead>
      <tbody>
        {pnlData == null ||
          pnlData.map((data) => <Row key={data.code} data={data} />)}
        {pnlData == null || (
          <tr className="border-t-2 border-black text-end">
            <td className="text-lg font-bold">Total:</td>
            <td>{totalTransaction?.toFixed(2)}</td>
            <td>{totalDividend?.toFixed(2)}</td>
            <td>{totalEarnings?.toFixed(2)}</td>
          </tr>
        )}
      </tbody>
    </table>
  );

  let loadedPage =
    pnlData == null || pnlData.length === 0 ? (
      <Card>
        <p className="text-lg font-semibold text-center">
          No Transaction Found
        </p>
      </Card>
    ) : (
      <>
        {totalEarnings == null || (
          <p className="my-4 md:my-8 ml-[10%] font-bold">{`Total Earnings: ${totalEarnings?.toFixed(2)}`}</p>
        )}
        {table}
      </>
    );

  return (
    <>
      <h1>Net Profit/Loss</h1>
      {pnlData == null ? <LoadingPage /> : loadedPage}
    </>
  );
}

function Row({ data }: { data: PNLReportLineItem }) {
  let { code, name, dividend_earnings, transaction_earnings } = data;

  return (
    <Link href={`/pnl/${code}`} passHref>
      <a
        key={code}
        className="table-row odd:bg-gray-50 even:bg-white hover:cursor-pointer hover:bg-blue-100"
      >
        <td>
          <p className="font-bold ">{name}</p>
          <p className="text-sm text-gray-700">{code}</p>
        </td>
        <td>{transaction_earnings.toFixed(2)}</td>
        <td>{dividend_earnings.toFixed(2)}</td>
        <td>{(transaction_earnings + dividend_earnings).toFixed(2)}</td>
      </a>
    </Link>
  );
}
