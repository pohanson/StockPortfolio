import { getCookie } from "cookies-next";
import TransactionFormPageFactory from "../../../components/transaction/form/TransactionFormPageFactory";

export default function EditTransactionPage({ data, transactionId }) {
  return TransactionFormPageFactory(true, data, transactionId);
}

export async function getServerSideProps({ req, params }) {
  let sessionid = getCookie("sessionid", { req });
  const { transactionId } = params;
  let data = await fetch(
    `${process.env.API_URL}/transaction/${transactionId}`,
    {
      headers: { Cookie: `sessionid=${sessionid}` },
    },
  ).then((r) => r.json());
  if ("error" in data) {
    return { redirect: { destination: "/login", permanent: false } };
  }
  return { props: { data, transactionId } };
}
