import traceback
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request, Query, Depends, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from html_render.service import process_wap_text
from wap_request.wap_request import get_httpx_client, close_httpx_client, request_wap
from wap_request.url_utils import ensure_http_scheme


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_httpx_client()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("static/index.html")


@app.get("/wml_to_html", response_class=HTMLResponse)
async def convert(
    request: Request,
    wml_url: str = Query(..., description="WML URL to convert"),
    client: httpx.AsyncClient = Depends(get_httpx_client),
):
    formatted_url = ensure_http_scheme(wml_url)
    try:
        status_code, text = await request_wap(client, formatted_url)
        if status_code >= 400:
            return templates.TemplateResponse(
                request=request,
                name="404.html",
                context={"url": formatted_url},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        representation = process_wap_text(text, base_url=formatted_url)
        return templates.TemplateResponse(
            request=request,
            name="convert.html",
            context={"document": representation},
        )
    except (httpx.RequestError, httpx.HTTPError, Exception) as e:
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"url": formatted_url},
            status_code=status.HTTP_404_NOT_FOUND,
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("warp_proxi:app", host="0.0.0.0", port=5000, reload=True)
