# Objective

- scrape data from "https://api.app.studiospace.com/listings/list-agencies",
- count collection of region services
- transform mutate to
```json
{
  "code": 200,
  "data": [
    {
      "regionCode": "AU",
      "services": [
        { "count": 88, "name": "Advertising, Brand & Creative" },
        { "count": 0, "name": "Media, PR & Events" },
        { "count": 114, "name": "others" }
      ]
    },
    {
      "regionCode": "GB",
      "services": [
        { "count": 403, "name": "Advertising, Brand & Creative" },
        { "count": 209, "name": "Media, PR & Events" },
        { "count": 1672, "name": "others" }
      ]
    },
    {
      "regionCode": "US",
      "services": [
        { "count": 43, "name": "Advertising, Brand & Creative" },
        { "count": 32, "name": "Media, PR & Events" },
        { "count": 86, "name": "others" }
      ]
    },
    {
      "regionCode": "OTHERS",
      "services": [
        { "count": 0, "name": "Advertising, Brand & Creative" },
        { "count": 0, "name": "Media, PR & Events" },
        { "count": 90, "name": "others" }
      ]
    }
  ],
  "message": "Data fetched successfully"
}
```

## Stack
- python
- python asyncio
- python typing
- flask

# Test Link
[Vercel](https://test-pacc-be.vercel.app/api/list-agencies)
