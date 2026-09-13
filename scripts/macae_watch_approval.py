"""One synthetic tester approval on the observed native plan; no model client."""
import asyncio,json,time
import httpx,websockets
async def main():
    base="http://127.0.0.1:3000/api/v4"
    sid="ptu-macae-cloud-91dfa4d3"
    uid="00000000-0000-0000-0000-000000000000"
    events=[]
    async with websockets.connect(base.replace("http","ws")+"/socket/"+sid+"?user_id="+uid) as ws:
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.post(base+"/plan_approval",headers={"x-ms-client-principal-id":uid},json={"m_plan_id":"2100d6d3-110f-4b44-a9e5-62d90f59e87c","plan_id":"82e5df2b-00a2-4a12-a248-af425f12caa6","approved":True,"feedback":"Synthetic tester approves the inspected HR and IT plan; no real business transactions."})
        result={"httpStatus":r.status_code,"response":r.json(),"events":events}
        end=time.monotonic()+180
        while r.status_code==200 and time.monotonic()<end:
            try: e=json.loads(await asyncio.wait_for(ws.recv(),timeout=max(1,end-time.monotonic())))
            except asyncio.TimeoutError: break
            events.append(e)
            print("MACAE_EVENT "+json.dumps(e),flush=True)
            if e.get("type") in ["user_clarification_request","final_result_message","error_message","timeout_notification"]: break
        print("MACAE_RESULT "+json.dumps({"name":"cloud-approval-events","data":result}),flush=True)
asyncio.run(main())
