# Assumptions and decisions log

These assumptions keep the team moving under a same-day deadline. Replace them with confirmed answers when backend/product owners are available; do not silently change the published API contract.

| Assumption | Decision now | Follow-up |
| --- | --- | --- |
| Primary prize | Best UI/UX is the primary goal, with data and DigitalOcean tracks supporting it. | Confirm team’s final submission emphasis. |
| Event deadline | The official page was checked on July 11, 2026 and showed 5:00pm PDT. | Verify directly in Devpost before submission. |
| DigitalOcean use | The frontend is a Static Site on App Platform; backend is a Web Service; AI inference uses DigitalOcean AI Platform. | Confirm available account/credits and selected model endpoint. |
| App architecture | Frontend is React/Vite/TS/Tailwind; backend is independently built behind REST endpoints. | Confirm backend language and app component settings. |
| Mock default | `VITE_USE_MOCK=true` until integration is proven. | Switch only after staging flow is tested. |
| File handling | Frontend accepts PDF/TXT; backend extracts text and discards temporary source files. | Set final upload size cap and retention policy. |
| `interests` format | Send selected causes as a JSON string in multipart form data. | Confirm exact backend parser behavior; the contract names the field but not its serialization. |
| SF data | Backend normalizes a selected SF Open Data source into the contract’s neighborhoods/categories. | Record the exact dataset/query/source URL in backend docs. |
| Freshness | Cached data is acceptable when labelled with its timestamp. | Set refresh cadence and cache TTL. |
| Demo data | Sample response data uses fictionalized organizations/opportunities unless verified partner listings are provided. | Replace only with accurate, permissioned listings. |
| Map | Map is optional and omitted until all core UX, deployment, and accessibility checks pass. | Add only if time remains. |
| Privacy | No accounts, analytics of resumes, or persistent browser storage are required for the hackathon demo. | Define consent/retention policy before any public launch. |
