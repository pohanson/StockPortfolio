import { getJsonHandler } from "../../../lib/baseApiHandler";

export default async function handler(req, res) {
  let code = req.query.code;
  console.log(req.method, `/api/pnl/${code}`);
  let [statusCode, json] = await getJsonHandler(
    process.env.API_URL + `/pnl/${code}`,
    req.headers.cookie,
  );
  res.status(statusCode).json(json);
}
