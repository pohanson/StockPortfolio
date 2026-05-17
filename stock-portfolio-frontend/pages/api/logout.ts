import { getJsonHandler } from "../../lib/baseApiHandler";

export default function logoutRoute(req, res) {
  getJsonHandler(
    process.env.API_URL + "/user/logout",
    req.headers.cookie || "",
  );
  res.redirect("/");
}
