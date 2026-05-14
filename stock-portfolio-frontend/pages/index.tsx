import { GetServerSideProps } from "next";

export default function ChecksRedirect() {
  return;
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  let res = await fetch(`${process.env.FRONTEND_SERVER_URL}/api/user`);
  let user = await res.json();
  if (user.isLogin) {
    return { redirect: { destination: "/portfolio", statusCode: 301 } };
  } else {
    return { redirect: { destination: "/login", statusCode: 301 } };
  }
};
