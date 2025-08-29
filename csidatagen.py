import random
import datetime
import csv
import sys
import io

# Column names extracted from the provided data
COLUMNS = [
    't', 'S_ConnectionDeviceId', 'S_CappingStationCapWeight', 'A_CappingStationComplete', 'A_CappingStationDuration',
    'A_CappingStationFinishTimeDay', 'A_CappingStationFinishTimeHour', 'A_CappingStationFinishTimeMicroSecond',
    'A_CappingStationFinishTimeMinute', 'A_CappingStationFinishTimeMonth', 'A_CappingStationFinishTimeSecond',
    'A_CappingStationFinishTimeYear', 'A_CappingStationOpRequired', 'A_CappingStationStartTimeDay',
    'A_CappingStationStartTimeHour', 'A_CappingStationStartTimeMicroSecond', 'A_CappingStationStartTimeMinute',
    'A_CappingStationStartTimeMonth', 'A_CappingStationStartTimeSecond', 'A_CappingStationStartTimeYear',
    'S_CurrentVehicleID', 'S_DryFillColor1CountDispensed', 'S_DryFillColor1CountRequired', 'S_DryFillColor2CountDispensed',
    'S_DryFillColor2CountRequired', 'S_DryFillColor3CountDispensed', 'S_DryFillColor3CountRequired', 'A_DryFillComplete',
    'A_DryFillDuration', 'A_DryFillFinishTimeDay', 'A_DryFillFinishTimeHour', 'A_DryFillFinishTimeMicroSecond',
    'A_DryFillFinishTimeMinute', 'A_DryFillFinishTimeMonth', 'A_DryFillFinishTimeSecond', 'A_DryFillFinishTimeYear',
    'A_DryFillOpRequired', 'S_DryFillPos1Color', 'S_DryFillPos2Color', 'S_DryFillPos3Color', 'S_DryFillPos4Color',
    'S_DryFillPos5Color', 'S_DryFillPos6Color', 'S_DryFillPos7Color', 'A_DryFillStartTimeDay', 'A_DryFillStartTimeHour',
    'A_DryFillStartTimeMicroSecond', 'A_DryFillStartTimeMinute', 'A_DryFillStartTimeMonth', 'A_DryFillStartTimeSecond',
    'A_DryFillStartTimeYear', 'A_InspectStationVisionComplete', 'S_InspectStationVisionDryFillCount',
    'S_InspectStationVisionDryFillCountBlu', 'S_InspectStationVisionDryFillCountRed', 'S_InspectStationVisionDryFillCountYel',
    'A_InspectStationVisionDuration', 'A_InspectStationVisionFinishTimeDay', 'A_InspectStationVisionFinishTimeHour',
    'A_InspectStationVisionFinishTimeMicroSecond', 'A_InspectStationVisionFinishTimeMinute',
    'A_InspectStationVisionFinishTimeMonth', 'A_InspectStationVisionFinishTimeSecond', 'A_InspectStationVisionFinishTimeYear',
    'A_InspectStationVisionOpRequired', 'S_InspectStationVisionPassFail', 'S_InspectStationVisionPos1Color',
    'S_InspectStationVisionPos2Color', 'S_InspectStationVisionPos3Color', 'S_InspectStationVisionPos4Color',
    'S_InspectStationVisionPos5Color', 'S_InspectStationVisionPos6Color', 'S_InspectStationVisionPos7Color',
    'A_InspectStationVisionStartTimeDay', 'A_InspectStationVisionStartTimeHour', 'A_InspectStationVisionStartTimeMicroSecond',
    'A_InspectStationVisionStartTimeMinute', 'A_InspectStationVisionStartTimeMonth', 'A_InspectStationVisionStartTimeSecond',
    'A_InspectStationVisionStartTimeYear', 'S_InspectStationVisionVialRGBBluLower', 'S_InspectStationVisionVialRGBBluUpper',
    'S_InspectStationVisionVialRGBBlue', 'S_InspectStationVisionVialRGBGreLower', 'S_InspectStationVisionVialRGBGreUpper',
    'S_InspectStationVisionVialRGBGreen', 'S_InspectStationVisionVialRGBRed', 'S_InspectStationVisionVialRGBRedLower',
    'S_InspectStationVisionVialRGBRedUpper', 'A_InspectStationVisionWaitonRobot', 'A_InspectStationWeighCheckComplete',
    'S_InspectStationWeighCheckData', 'A_InspectStationWeighCheckDuration', 'A_InspectStationWeighCheckFinishTimeDay',
    'A_InspectStationWeighCheckFinishTimeHour', 'A_InspectStationWeighCheckFinishTimeMicroSecond',
    'A_InspectStationWeighCheckFinishTimeMinute', 'A_InspectStationWeighCheckFinishTimeMonth',
    'A_InspectStationWeighCheckFinishTimeSecond', 'A_InspectStationWeighCheckFinishTimeYear',
    'S_InspectStationWeighCheckLowerLimit', 'A_InspectStationWeighCheckOpRequired', 'S_InspectStationWeighCheckPassFail',
    'A_InspectStationWeighCheckStartTimeDay', 'A_InspectStationWeighCheckStartTimeHour',
    'A_InspectStationWeighCheckStartTimeMicroSecond', 'A_InspectStationWeighCheckStartTimeMinute',
    'A_InspectStationWeighCheckStartTimeMonth', 'A_InspectStationWeighCheckStartTimeSecond',
    'A_InspectStationWeighCheckStartTimeYear', 'S_InspectStationWeighCheckUpperLimit', 'A_InspectStationWeighCheckWaitonRobot',
    'S_MESScheduleUniqueID', 'S_ManualRecipeNumber', 'A_ProcessDuration', 'A_ProcessFinishTimeDay', 'A_ProcessFinishTimeHour',
    'A_ProcessFinishTimeMicroSecond', 'A_ProcessFinishTimeMinute', 'A_ProcessFinishTimeMonth', 'A_ProcessFinishTimeSecond',
    'A_ProcessFinishTimeYear', 'A_ProcessStartTimeDay', 'A_ProcessStartTimeHour', 'A_ProcessStartTimeMicroSecond',
    'A_ProcessStartTimeMinute', 'A_ProcessStartTimeMonth', 'A_ProcessStartTimeSecond', 'A_ProcessStartTimeYear',
    'A_Station1ChecknLoadDuration', 'A_Station1FinishTimeDay', 'A_Station1FinishTimeHour', 'A_Station1FinishTimeMicroSecond',
    'A_Station1FinishTimeMinute', 'A_Station1FinishTimeMonth', 'A_Station1FinishTimeSecond', 'A_Station1FinishTimeYear',
    'A_Station1StartTimeDay', 'A_Station1StartTimeHour', 'A_Station1StartTimeMicroSecond', 'A_Station1StartTimeMinute',
    'A_Station1StartTimeMonth', 'A_Station1StartTimeSecond', 'A_Station1StartTimeYear', 'A_Station9FinishTimeDay',
    'A_Station9FinishTimeHour', 'A_Station9FinishTimeMicroSecond', 'A_Station9FinishTimeMinute', 'A_Station9FinishTimeMonth',
    'A_Station9FinishTimeSecond', 'A_Station9FinishTimeYear', 'A_Station9RejectDuration', 'A_Station9StartTimeDay',
    'A_Station9StartTimeHour', 'A_Station9StartTimeMicroSecond', 'A_Station9StartTimeMinute', 'A_Station9StartTimeMonth',
    'A_Station9StartTimeSecond', 'A_Station9StartTimeYear', 'A_Station9WaitonRobot', 'A_UnloadDuration',
    'A_UnloadFinishTimeDay', 'A_UnloadFinishTimeHour', 'A_UnloadFinishTimeMicroSecond', 'A_UnloadFinishTimeMinute',
    'A_UnloadFinishTimeMonth', 'A_UnloadFinishTimeSecond', 'A_UnloadFinishTimeYear', 'A_UnloadStartTimeDay',
    'A_UnloadStartTimeHour', 'A_UnloadStartTimeMicroSecond', 'A_UnloadStartTimeMinute', 'A_UnloadStartTimeMonth',
    'A_UnloadStartTimeSecond', 'A_UnloadStartTimeYear', 'A_VialBCRReadDuration', 'A_VialBCRReadFinishTimeDay',
    'A_VialBCRReadFinishTimeHour', 'A_VialBCRReadFinishTimeMicroSecond', 'A_VialBCRReadFinishTimeMinute',
    'A_VialBCRReadFinishTimeMonth', 'A_VialBCRReadFinishTimeSecond', 'A_VialBCRReadFinishTimeYear',
    'A_VialBCRReadStartTimeDay', 'A_VialBCRReadStartTimeHour', 'A_VialBCRReadStartTimeMicroSecond',
    'A_VialBCRReadStartTimeMinute', 'A_VialBCRReadStartTimeMonth', 'A_VialBCRReadStartTimeSecond',
    'A_VialBCRReadStartTimeYear', 'S_VialBCRReadVialBarCodeString', 'A_VialDamageInspectDuration',
    'A_VialDamageInspectFinishTimeDay', 'A_VialDamageInspectFinishTimeHour', 'A_VialDamageInspectFinishTimeMicroSecond',
    'A_VialDamageInspectFinishTimeMinute', 'A_VialDamageInspectFinishTimeMonth', 'A_VialDamageInspectFinishTimeSecond',
    'A_VialDamageInspectFinishTimeYear', 'A_VialDamageInspectStartTimeDay', 'A_VialDamageInspectStartTimeHour',
    'A_VialDamageInspectStartTimeMicroSecond', 'A_VialDamageInspectStartTimeMinute', 'A_VialDamageInspectStartTimeMonth',
    'A_VialDamageInspectStartTimeSecond', 'A_VialDamageInspectStartTimeYear', 'S_VialEmptyWeight',
    'A_WetFillStation3Complete', 'A_WetFillStation3Duration', 'A_WetFillStation3FinishTimeDay',
    'A_WetFillStation3FinishTimeHour', 'A_WetFillStation3FinishTimeMicroSecond', 'A_WetFillStation3FinishTimeMinute',
    'A_WetFillStation3FinishTimeMonth', 'A_WetFillStation3FinishTimeSecond', 'A_WetFillStation3FinishTimeYear',
    'A_WetFillStation3OpRequired', 'A_WetFillStation3StartTimeDay', 'A_WetFillStation3StartTimeHour',
    'A_WetFillStation3StartTimeMicroSecond', 'A_WetFillStation3StartTimeMinute', 'A_WetFillStation3StartTimeMonth',
    'A_WetFillStation3StartTimeSecond', 'A_WetFillStation3StartTimeYear', 'S_WetFillStation3VolumeDispTank1',
    'S_WetFillStation3VolumeDispTank2', 'S_WetFillStation3VolumeDispTank3', 'S_WetFillStation3VolumeDispTank4',
    'S_WetFillStation3VolumeReqTank1', 'S_WetFillStation3VolumeReqTank2', 'S_WetFillStation3VolumeReqTank3',
    'S_WetFillStation3VolumeReqTank4', 'A_WetFillStation4Complete', 'A_WetFillStation4Duration',
    'A_WetFillStation4FinishTimeDay', 'A_WetFillStation4FinishTimeHour', 'A_WetFillStation4FinishTimeMicroSecond',
    'A_WetFillStation4FinishTimeMinute', 'A_WetFillStation4FinishTimeMonth', 'A_WetFillStation4FinishTimeSecond',
    'A_WetFillStation4FinishTimeYear', 'A_WetFillStation4OpRequired', 'A_WetFillStation4StartTimeDay',
    'A_WetFillStation4StartTimeHour', 'A_WetFillStation4StartTimeMicroSecond', 'A_WetFillStation4StartTimeMinute',
    'A_WetFillStation4StartTimeMonth', 'A_WetFillStation4StartTimeSecond', 'A_WetFillStation4StartTimeYear',
    'S_WetFillStation4VolumeDispTank1', 'S_WetFillStation4VolumeDispTank2', 'S_WetFillStation4VolumeDispTank3',
    'S_WetFillStation4VolumeDispTank4', 'S_WetFillStation4VolumeReqTank1', 'S_WetFillStation4VolumeReqTank2',
    'S_WetFillStation4VolumeReqTank3', 'S_WetFillStation4VolumeReqTank4', 'A_WetFillStation5Complete',
    'A_WetFillStation5Nozzle1Duration', 'A_WetFillStation5Nozzle1FinishTimeDay', 'A_WetFillStation5Nozzle1FinishTimeHour',
    'A_WetFillStation5Nozzle1FinishTimeMicroSecond', 'A_WetFillStation5Nozzle1FinishTimeMinute',
    'A_WetFillStation5Nozzle1FinishTimeMonth', 'A_WetFillStation5Nozzle1FinishTimeSecond',
    'A_WetFillStation5Nozzle1FinishTimeYear', 'A_WetFillStation5Nozzle1StartTimeDay', 'A_WetFillStation5Nozzle1StartTimeHour',
    'A_WetFillStation5Nozzle1StartTimeMicroSecond', 'A_WetFillStation5Nozzle1StartTimeMinute',
    'A_WetFillStation5Nozzle1StartTimeMonth', 'A_WetFillStation5Nozzle1StartTimeSecond',
    'A_WetFillStation5Nozzle1StartTimeYear', 'A_WetFillStation5Nozzle2Duration', 'A_WetFillStation5Nozzle2FinishTimeDay',
    'A_WetFillStation5Nozzle2FinishTimeHour', 'A_WetFillStation5Nozzle2FinishTimeMicroSecond',
    'A_WetFillStation5Nozzle2FinishTimeMinute', 'A_WetFillStation5Nozzle2FinishTimeMonth',
    'A_WetFillStation5Nozzle2FinishTimeSecond', 'A_WetFillStation5Nozzle2FinishTimeYear',
    'A_WetFillStation5Nozzle2StartTimeDay', 'A_WetFillStation5Nozzle2StartTimeHour',
    'A_WetFillStation5Nozzle2StartTimeMicroSecond', 'A_WetFillStation5Nozzle2StartTimeMinute',
    'A_WetFillStation5Nozzle2StartTimeMonth', 'A_WetFillStation5Nozzle2StartTimeSecond',
    'A_WetFillStation5Nozzle2StartTimeYear', 'A_WetFillStation5Nozzle3FinishTimeDay', 'A_WetFillStation5Nozzle3FinishTimeHour',
    'A_WetFillStation5Nozzle3FinishTimeMicroSecond', 'A_WetFillStation5Nozzle3FinishTimeMinute',
    'A_WetFillStation5Nozzle3FinishTimeMonth', 'A_WetFillStation5Nozzle3FinishTimeSecond',
    'A_WetFillStation5Nozzle3FinishTimeYear', 'A_WetFillStation5Nozzle3Nozzle3Duration', 'A_WetFillStation5Nozzle3StartTimeDay',
    'A_WetFillStation5Nozzle3StartTimeHour', 'A_WetFillStation5Nozzle3StartTimeMicroSecond',
    'A_WetFillStation5Nozzle3StartTimeMinute', 'A_WetFillStation5Nozzle3StartTimeMonth',
    'A_WetFillStation5Nozzle3StartTimeSecond', 'A_WetFillStation5Nozzle3StartTimeYear', 'A_WetFillStation5Nozzle4FinishTimeDay',
    'A_WetFillStation5Nozzle4FinishTimeHour', 'A_WetFillStation5Nozzle4FinishTimeMicroSecond',
    'A_WetFillStation5Nozzle4FinishTimeMinute', 'A_WetFillStation5Nozzle4FinishTimeMonth',
    'A_WetFillStation5Nozzle4FinishTimeSecond', 'A_WetFillStation5Nozzle4FinishTimeYear',
    'A_WetFillStation5Nozzle4Nozzle4Duration', 'A_WetFillStation5Nozzle4StartTimeDay', 'A_WetFillStation5Nozzle4StartTimeHour',
    'A_WetFillStation5Nozzle4StartTimeMicroSecond', 'A_WetFillStation5Nozzle4StartTimeMinute',
    'A_WetFillStation5Nozzle4StartTimeMonth', 'A_WetFillStation5Nozzle4StartTimeSecond',
    'A_WetFillStation5Nozzle4StartTimeYear', 'A_WetFillStation5OpRequired', 'S_WetFillStation5VolumeDispTank1',
    'S_WetFillStation5VolumeDispTank2', 'S_WetFillStation5VolumeDispTank3', 'S_WetFillStation5VolumeDispTank4',
    'S_WetFillStation5VolumeReqTank1', 'S_WetFillStation5VolumeReqTank2', 'S_WetFillStation5VolumeReqTank3',
    'S_WetFillStation5VolumeReqTank4'
]

# Configurable parameters (you can modify these)
CONFIG = {
    'num_rows': 50000,  # Number of rows to generate
    'start_timestamp': datetime.datetime(2023, 4, 4, 0, 37, 13),  # Starting timestamp
    'timestamp_increment_min': 10,  # Minimum seconds between rows
    'timestamp_increment_max': 120,  # Maximum seconds between rows
    'device_id': 'ftedge_gateway_01',  # Fixed device ID
    'vehicle_id_range': (1, 20),  # Range for CurrentVehicleID
    'duration_range': (0, 200000),  # General range for durations (e.g., DryFillDuration)
    'count_range': (0, 5),  # For counts like DryFillColor1CountDispensed
    'color_range': (0, 255),  # For colors like DryFillPos1Color
    'weight_range': (30.0, 110.0),  # For weights like InspectStationWeighCheckData
    'volume_range': (0.0, 25.0),  # For volumes like WetFillStation3VolumeDispTank1
    'complete_flags': [0, 1],  # For complete flags like DryFillComplete
    'pass_fail': [0, 1, 2],  # For pass/fail like InspectStationVisionPassFail
    'op_required': [0, 1],  # For op required flags
    'inspection_bypassed_prob': 0.9,  # Probability of "Vial Inspection Bypassed" string
    'schedule_id_range': (500000000, 700000000),  # For MESScheduleUniqueID
    'recipe_number_range': (0, 5),  # For ManualRecipeNumber
}

def generate_timestamp(current_ts):
    increment = random.randint(CONFIG['timestamp_increment_min'], CONFIG['timestamp_increment_max'])
    return current_ts + datetime.timedelta(seconds=increment)

def generate_time_components(ts):
    return {
        'Day': ts.day,
        'Hour': ts.hour,
        'MicroSecond': random.randint(0, 999999),  # Often random in samples
        'Minute': ts.minute,
        'Month': ts.month,
        'Second': ts.second,
        'Year': ts.year
    }

def generate_row(current_ts):
    ts_str = current_ts.isoformat() + 'Z'  # Format like '2023-04-04T00:37:13.538Z'
    row = {}
    time_comp = generate_time_components(current_ts)

    # Timestamp
    row['t'] = ts_str

    # Fixed or simple fields
    row['S_ConnectionDeviceId'] = CONFIG['device_id']
    row['S_CurrentVehicleID'] = random.randint(*CONFIG['vehicle_id_range'])

    # Capping station (mostly 0 in samples, but some durations)
    row['S_CappingStationCapWeight'] = 0
    row['A_CappingStationComplete'] = random.choice(CONFIG['complete_flags'])
    row['A_CappingStationDuration'] = random.randint(*CONFIG['duration_range']) if row['A_CappingStationComplete'] else 0
    for prefix in ['A_CappingStationFinishTime', 'A_CappingStationStartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp] + random.randint(-1, 1) if random.random() > 0.5 else 0
    row['A_CappingStationOpRequired'] = random.choice(CONFIG['op_required'])

    # Dry fill
    row['A_DryFillComplete'] = random.choice(CONFIG['complete_flags'])
    row['A_DryFillDuration'] = random.randint(*CONFIG['duration_range'])
    for i in range(1, 4):
        row[f'S_DryFillColor{i}CountDispensed'] = random.randint(*CONFIG['count_range'])
        row[f'S_DryFillColor{i}CountRequired'] = random.randint(*CONFIG['count_range'])
    row['A_DryFillOpRequired'] = random.choice(CONFIG['op_required'])
    for i in range(1, 8):
        row[f'S_DryFillPos{i}Color'] = random.randint(*CONFIG['color_range'])
    for prefix in ['A_DryFillFinishTime', 'A_DryFillStartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp] + random.randint(-1, 1)

    # Inspect station vision
    row['A_InspectStationVisionComplete'] = random.choice(CONFIG['complete_flags'])
    row['S_InspectStationVisionDryFillCount'] = random.randint(0, 10)
    for color in ['Blu', 'Red', 'Yel']:
        row[f'S_InspectStationVisionDryFillCount{color}'] = random.randint(0, 5)
    row['A_InspectStationVisionDuration'] = random.randint(*CONFIG['duration_range'])
    row['A_InspectStationVisionOpRequired'] = random.choice(CONFIG['op_required'])
    row['S_InspectStationVisionPassFail'] = random.choice(CONFIG['pass_fail'])
    for i in range(1, 8):
        row[f'S_InspectStationVisionPos{i}Color'] = random.randint(*CONFIG['color_range'])
    for prefix in ['A_InspectStationVisionFinishTime', 'A_InspectStationVisionStartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp] + random.randint(-1, 1)
    for comp in ['BluLower', 'BluUpper', 'GreLower', 'GreUpper', 'RedLower', 'RedUpper']:
        row[f'S_InspectStationVisionVialRGB{comp}'] = random.randint(0, 255)
    for comp in ['Blue', 'Green', 'Red']:
        row[f'S_InspectStationVisionVialRGB{comp}'] = random.randint(0, 255)
    row['A_InspectStationVisionWaitonRobot'] = 0  # Often 0

    # Weigh check
    row['A_InspectStationWeighCheckComplete'] = random.choice(CONFIG['complete_flags'])
    row['S_InspectStationWeighCheckData'] = round(random.uniform(*CONFIG['weight_range']), 3)
    row['A_InspectStationWeighCheckDuration'] = random.randint(*CONFIG['duration_range'])
    row['S_InspectStationWeighCheckLowerLimit'] = 0
    row['S_InspectStationWeighCheckUpperLimit'] = random.randint(1, 999)
    row['A_InspectStationWeighCheckOpRequired'] = random.choice(CONFIG['op_required'])
    row['S_InspectStationWeighCheckPassFail'] = random.choice(CONFIG['pass_fail'])
    row['A_InspectStationWeighCheckWaitonRobot'] = 0
    for prefix in ['A_InspectStationWeighCheckFinishTime', 'A_InspectStationWeighCheckStartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp] + random.randint(-1, 1)

    # MES and process
    row['S_MESScheduleUniqueID'] = random.randint(*CONFIG['schedule_id_range'])
    row['S_ManualRecipeNumber'] = random.randint(*CONFIG['recipe_number_range'])
    row['A_ProcessDuration'] = random.randint(0, 1000000)
    for prefix in ['A_ProcessFinishTime', 'A_ProcessStartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp] + random.randint(-2, 2)

    # Station 1 and 9
    row['A_Station1ChecknLoadDuration'] = random.randint(*CONFIG['duration_range'])
    for prefix in ['A_Station1FinishTime', 'A_Station1StartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp]
    for prefix in ['A_Station9FinishTime', 'A_Station9StartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp]
    row['A_Station9RejectDuration'] = random.randint(*CONFIG['duration_range'])
    row['A_Station9WaitonRobot'] = 0

    # Unload
    row['A_UnloadDuration'] = random.randint(*CONFIG['duration_range'])
    for prefix in ['A_UnloadFinishTime', 'A_UnloadStartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp]

    # Vial BCR and Damage
    row['A_VialBCRReadDuration'] = random.randint(*CONFIG['duration_range'])
    for prefix in ['A_VialBCRReadFinishTime', 'A_VialBCRReadStartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp]
    row['S_VialBCRReadVialBarCodeString'] = ''  # Empty in samples
    row['A_VialDamageInspectDuration'] = random.randint(*CONFIG['duration_range'])
    for prefix in ['A_VialDamageInspectFinishTime', 'A_VialDamageInspectStartTime']:
        for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
            row[f'{prefix}{comp}'] = time_comp[comp]
    row['S_VialEmptyWeight'] = round(random.uniform(0, 0.1), 2) if random.random() > 0.5 else 'Vial Inspection Bypassed' if random.random() < CONFIG['inspection_bypassed_prob'] else 0

    # Additional Vial fields
    row['S_VialBCRReadIsOK'] = random.choice([0, 1])
    row['S_VialDamageLowerLimit'] = random.randint(0, 100)
    row['S_VialDamageUpperLimit'] = random.randint(101, 500)

    # Wet fill stations 3,4,5
    for station in [3, 4]:
        row[f'A_WetFillStation{station}Complete'] = random.choice(CONFIG['complete_flags'])
        row[f'A_WetFillStation{station}Duration'] = random.randint(*CONFIG['duration_range'])
        row[f'A_WetFillStation{station}OpRequired'] = random.choice(CONFIG['op_required'])
        for prefix in [f'A_WetFillStation{station}FinishTime', f'A_WetFillStation{station}StartTime']:
            for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
                row[f'{prefix}{comp}'] = time_comp[comp]
        for tank in range(1, 5):
            row[f'S_WetFillStation{station}VolumeDispTank{tank}'] = round(random.uniform(*CONFIG['volume_range']), 3)
            row[f'S_WetFillStation{station}VolumeReqTank{tank}'] = round(random.uniform(*CONFIG['volume_range']), 3)

    # Station 5 is more complex with nozzles
    row['A_WetFillStation5Complete'] = random.choice(CONFIG['complete_flags'])
    row['A_WetFillStation5OpRequired'] = random.choice(CONFIG['op_required'])
    for nozzle in range(1, 5):
        duration_key = f'A_WetFillStation5Nozzle{nozzle}Duration' if nozzle <= 2 else f'A_WetFillStation5Nozzle{nozzle}Nozzle{nozzle}Duration'
        row[duration_key] = random.randint(*CONFIG['duration_range'])
        for prefix in [f'A_WetFillStation5Nozzle{nozzle}FinishTime', f'A_WetFillStation5Nozzle{nozzle}StartTime']:
            for comp in ['Day', 'Hour', 'MicroSecond', 'Minute', 'Month', 'Second', 'Year']:
                row[f'{prefix}{comp}'] = time_comp[comp]
    for tank in range(1, 5):
        row[f'S_WetFillStation5VolumeDispTank{tank}'] = round(random.uniform(*CONFIG['volume_range']), 3)
        row[f'S_WetFillStation5VolumeReqTank{tank}'] = round(random.uniform(*CONFIG['volume_range']), 3)

    # Fill any missing columns with 0 (as many are 0 in samples)
    for col in COLUMNS:
        if col not in row:
            row[col] = 0

    return [row.get(col, '') for col in COLUMNS]

def generate_csv(num_rows, output_file=None):
    output = io.StringIO() if output_file is None else open(output_file, 'w', newline='')
    writer = csv.writer(output)
    writer.writerow(COLUMNS)  # Header

    current_ts = CONFIG['start_timestamp']
    for _ in range(num_rows):
        row = generate_row(current_ts)
        writer.writerow(row)
        current_ts = generate_timestamp(current_ts)

    if output_file is None:
        return output.getvalue()
    else:
        output.close()

# Example usage: generate to stdout
if __name__ == '__main__':
    # Generate to stdout (no file creation)
    csv_data = generate_csv(CONFIG['num_rows'], output_file="csidatagen.csv")
    sys.stdout.write(csv_data)