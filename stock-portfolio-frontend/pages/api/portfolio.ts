import { NextApiRequest } from "next";
import { getJsonHandler } from "../../lib/baseApiHandler";

export default async function handler(req: NextApiRequest, res) {
  console.log(req.method, "/api/portfolio");
  let [statusCode, json] = await getJsonHandler(
    process.env.API_URL + `/portfolio`,
    req.headers.cookie || "",
  );
  res.status(statusCode).json(json);
}
