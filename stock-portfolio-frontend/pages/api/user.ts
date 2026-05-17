import { getJsonHandler } from "../../lib/baseApiHandler";

export default async function handler(req, res) {
  console.log(req.method, "/api/user");
  let [statusCode, json] = await getJsonHandler(
    process.env.API_URL + "/user",
    req.headers.cookie || "",
  );
  res.status(statusCode).json(json);
}
