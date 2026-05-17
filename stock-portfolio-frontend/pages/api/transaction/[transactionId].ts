import {
  deleteJsonHandler,
  getJsonHandler,
  putJsonHandler,
} from "../../../lib/baseApiHandler";

export default async function handler(req, res) {
  let { transactionId } = req.query;
  console.log(req.method, `/api/transaction/${transactionId}`);
  let statusCode, json;
  switch (req.method) {
    case "GET":
      [statusCode, json] = await getJsonHandler(
        process.env.API_URL + `/transaction/${transactionId}`,
        req.headers.cookie,
      );
      break;
    case "PUT":
      [statusCode, json] = await putJsonHandler(
        process.env.API_URL + `/transaction/${transactionId}`,
        req.body,
        req.headers.cookie,
      );
      break;
    case "DELETE":
      [statusCode, json] = await deleteJsonHandler(
        process.env.API_URL + `/transaction/${transactionId}`,
        req.headers.cookie,
      );
      break;
  }
  res.status(statusCode).json(json);
}
