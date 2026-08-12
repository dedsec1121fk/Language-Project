def shape:
  if type == "object" then {type:"object", keys:(keys|length), fields:(to_entries|map({key:.key,type:(.value|type)}))}
  elif type == "array" then {type:"array", length:length, sample_types:(map(type)|unique)}
  else {type:type, value:.} end;
shape
