import { GetServerSideProps } from "next/types";
import { getJsonHandler } from "../lib/baseApiHandler";

export default function ChecksRedirect() {
  return;
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  let [statusCode, user] = await getJsonHandler(
    `${process.env.FRONTEND_SERVER_URL}/api/user`,
    context.req.headers.cookie || "",
  );
  if (user.isLogin) {
    return { redirect: { destination: "/portfolio", statusCode: 301 } };
  } else {
    return { redirect: { destination: "/login", statusCode: 301 } };
  }
};
