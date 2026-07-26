import traceback
from fastapi import FastAPI, Request, Query, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from html_render.service import process_wap_request

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("static/index.html")


@app.get("/wml_to_html", response_class=HTMLResponse)
async def convert(request: Request, wml_url: str = Query(..., description="WML URL to convert")):
    try:
        representation = await process_wap_request(wml_url)
        return templates.TemplateResponse(
            request=request,
            name="convert.html",
            context={"document": representation},
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("warp_proxi:app", host="0.0.0.0", port=5000, reload=True)
