from fastapi import APIRouter, Depends
from models.schema import InputParameters
from rpc.rpc_client import CountNPVClient
from settings import Settings, get_settings

router = APIRouter()


@router.post('/calculate/',
             summary='Расчет NPV',
             tags=['counts'])
async def get_npv_result(input_data: InputParameters,
                         settings: Settings = Depends(get_settings)) -> str:
    npv_rpc = await CountNPVClient().connect(settings)
    response = await npv_rpc.call(input_data.year, input_data.percent)
    return response
