select distinct count(*), 
        strikes->'strikes'->>3 as seq 
from public."games" 
where playername = 'marinmarin1950' 
and strikes->'strikes'->>0  like '%1. e4%d5%' 
and strikes->'strikes'->>1  like '%2. d3%e6%' 
and strikes->'strikes'->>2  like '%3. Nf3%Nf6%' 
and color != strikes->>'winner' 
group by seq order by 1 desc