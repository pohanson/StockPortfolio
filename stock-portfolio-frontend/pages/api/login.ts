import { NextApiResponse } from "next/types";

export default async function loginRoute(req, res: NextApiResponse) {
  // get user from database then
  console.log(req.method, "/api/login");
  await fetch(process.env.API_URL + "/user", {
    method: "POST",
    body: JSON.stringify(req.body),
    headers: {
      "Content-Type": "application/json",
    },
  }).then(async (r) => {
    console.log(r.headers);
    if (r.status == 200) {
      res
        .setHeader("Set-Cookie", r.headers.get("set-cookie") || "")
        .json(await r.json());
    } else {
      res.status(r.status).json(await r.json());
    }
  });
}
