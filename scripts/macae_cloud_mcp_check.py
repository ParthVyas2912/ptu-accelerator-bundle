import asyncio,json,hashlib
from fastmcp import Client
async def main():
    async with Client("http://127.0.0.1:9000/hr/mcp") as c:
        tools=await c.list_tools()
        texts=[]
        for _ in range(2):
            r=await c.call_tool("get_workflow_blueprint",{"workflow":"employee_onboarding"})
            texts.append("\n".join(x.text for x in r.content if hasattr(x,"text")))
        error={}
        try:
            r=await c.call_tool("ptu_macae_unavailable_tool",{})
            error={"isError":r.is_error}
        except Exception as e:
            error={"exception":type(e).__name__,"message":str(e)}
        d={"toolNames":[t.name for t in tools],"workflow":"employee_onboarding","sameRepeatedBlueprint":texts[0]==texts[1],"blueprintCharacters":len(texts[0]),"blueprintSha256":hashlib.sha256(texts[0].encode()).hexdigest(),"unavailableTool":error,"modelCalls":0}
        print("MACAE_RESULT "+json.dumps({"name":"cloud-mcp-check","data":d}))
asyncio.run(main())
