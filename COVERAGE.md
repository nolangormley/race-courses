# Coverage

Weekly crawl of 2026-11-06: 294 races, 464 events, 55 courses published (12%).

| Status | Events | Meaning |
| --- | ---: | --- |
| ok | 45 | Course found; length within 3% of the race distance. |
| warn | 10 | Course found; check it (length within 8%, or joined from part of a larger map). |
| unsupported | 339 | Only a map type the crawler cannot read (PDF, image, Strava, ...). |
| no-source | 31 | No course map found on the organizer's site. |
| no-match | 20 | Maps found, but no line matches the race distance. |
| reject | 3 | A line matches, but it failed a check. |
| error | 16 | The site could not be read (robots.txt, blocked, or down). |

Map types on pages without a readable course: image 276, pdf 209, googlemaps 79, mapmyrun 39, ridewithgps 13, plotaroute 13, garmin 12, strava 5, arcgis 1, onthegomap 1.

## Not covered yet

A traced GPX in `manual/` can cover any of these; see the README.

| State | Race | Event | Status | Detail |
| --- | --- | --- | --- | --- |
| AK | [Anchorage Mayor's Marathon & Half Marathon](https://www.anchoragemayorsmarathon.com/Race/MayorsMarathon/Page/half) | Half Marathon | unsupported | only arcgis, image, pdf |
| AL | [Cotton Row Run](https://runsignup.com/Race/CottonRowRun/Page-5) | 10K | unsupported | only image |
| AL | [Cotton Row Run](https://runsignup.com/Race/CottonRowRun/Page-5) | 5K | unsupported | only image |
| AR | [Little Rock Marathon](https://littlerockmarathon.com/course/) | 10K | no-match | no line near 10.00 km in https://www.google.com/maps/d/kml?mid=16ZNA0DtAiFasUEP0zLTa398zbdM&forcekml=1 |
| AR | [Little Rock Marathon](https://littlerockmarathon.com/course/) | 5K | no-match | no line near 5.00 km in https://www.google.com/maps/d/kml?mid=16ZNA0DtAiFasUEP0zLTa398zbdM&forcekml=1 |
| AR | [Little Rock Marathon](https://littlerockmarathon.com/course/) | Half Marathon | no-match | no line near 21.10 km in https://www.google.com/maps/d/kml?mid=16ZNA0DtAiFasUEP0zLTa398zbdM&forcekml=1 |
| AR | [Little Rock Marathon](https://littlerockmarathon.com/course/) | Marathon | no-match | no line near 42.20 km in https://www.google.com/maps/d/kml?mid=16ZNA0DtAiFasUEP0zLTa398zbdM&forcekml=1 |
| AZ | [Mesa Marathon](https://mesamarathon.com/info?tab=course) | Marathon | unsupported | only googlemaps, image |
| AZ | [Pat's Run](https://pattillmanfoundation.org/pats-run/) | 4.2 Mile | no-source | no course map on https://pattillmanfoundation.org/pats-run/ |
| AZ | [Phoenix Marathon](https://phxmarathon.com/info?tab=course) | Marathon | unsupported | only googlemaps, image |
| CA | [Bay to Breakers](https://www.baytobreakers.com/12k) | 12K | unsupported | only image |
| CA | [Berkeley Half Marathon](https://berkeleyhalfmarathon.com/the-races/berkeley-half-10k-race/) | 10K | unsupported | only googlemaps, image, pdf |
| CA | [Berkeley Half Marathon](https://berkeleyhalfmarathon.com/the-races/5-k/) | 5K | unsupported | only googlemaps, image, pdf |
| CA | [Berkeley Half Marathon](https://berkeleyhalfmarathon.com/the-races/half-marathon/) | Half Marathon | unsupported | only image, pdf |
| CA | [Big Sur International Marathon](https://www.bigsurmarathon.org/races/11-miler/) | 11 Mile | unsupported | only pdf |
| CA | [Big Sur International Marathon](https://www.bigsurmarathon.org/races/marathon/) | Marathon | unsupported | only pdf |
| CA | [Carlsbad Marathon](https://inmotionevents.com/event/carlsbad-marathon/) | 5K | unsupported | only image, pdf |
| CA | [Carlsbad Marathon](https://inmotionevents.com/event/carlsbad-marathon/) | Half Marathon | unsupported | only image, pdf |
| CA | [Carlsbad Marathon](https://inmotionevents.com/event/carlsbad-marathon/) | Marathon | unsupported | only image, pdf |
| CA | [Dana Point Turkey Trot](https://www.turkeytrot.com/course-maps) | 10K | unsupported | only image |
| CA | [Dana Point Turkey Trot](https://www.turkeytrot.com/course-maps) | 5K | unsupported | only image |
| CA | [Disneyland Half Marathon](https://www.rundisney.com/events/disneyland/disneyland-half-marathon-weekend/) | Half Marathon | error | HTTP 403: https://www.rundisney.com/events/disneyland/disneyland-half-marathon-weekend/ |
| CA | [Disneyland Halloween Half Marathon](https://www.rundisney.com/events/disneyland/disneyland-halloween-half-marathon-weekend/) | 10K | error | HTTP 403: https://www.rundisney.com/events/disneyland/disneyland-halloween-half-marathon-weekend/ |
| CA | [Disneyland Halloween Half Marathon](https://www.rundisney.com/events/disneyland/disneyland-halloween-half-marathon-weekend/) | Half Marathon | error | HTTP 403: https://www.rundisney.com/events/disneyland/disneyland-halloween-half-marathon-weekend/ |
| CA | [La Jolla Half Marathon](https://lajollahalfmarathon.com/san-diego-running-races/5k/) | 5K | unsupported | only googlemaps, image |
| CA | [La Jolla Half Marathon](https://lajollahalfmarathon.com/san-diego-running-races/half-marathon/) | Half Marathon | unsupported | only googlemaps, image |
| CA | [Long Beach Marathon](https://www.runlongbeach.com/half-marathon) | Half Marathon | unsupported | only image |
| CA | [Long Beach Marathon](https://www.runlongbeach.com/marathon) | Marathon | unsupported | only image |
| CA | [Los Angeles Marathon](https://www.mccourtfoundation.org/event/los-angeles-marathon/distances-courses/) | LA 5K | unsupported | only image, pdf |
| CA | [Los Angeles Marathon](https://www.mccourtfoundation.org/event/los-angeles-marathon/distances-courses/) | Marathon | unsupported | only image, pdf |
| CA | [Monterey Bay Half Marathon](https://www.montereybayhalfmarathon.org/maps/) | Half Marathon | unsupported | only image, pdf |
| CA | [Napa Valley Marathon](https://napavalleymarathon.org/race-information/) | Half Marathon | unsupported | only pdf |
| CA | [Napa Valley Marathon](https://napavalleymarathon.org/race-information/) | Marathon | unsupported | only pdf |
| CA | [Oakland Marathon](https://oaklandmarathon.com/races/10k/) | 10K | unsupported | only image, mapmyrun, pdf |
| CA | [Oakland Marathon](https://oaklandmarathon.com/races/5k/) | 5K | unsupported | only image, mapmyrun, pdf |
| CA | [Oakland Marathon](https://oaklandmarathon.com/races/half/) | Half Marathon | unsupported | only image, mapmyrun, pdf |
| CA | [OC Marathon](https://ocmarathon.com/hoag-oc-5k/) | 5K | unsupported | only image |
| CA | [OC Marathon](https://ocmarathon.com/half-marathon/) | Marathon | no-match | no line near 42.20 km in https://www.google.com/maps/d/kml?mid=1JPnNxSqBMYc3B6aN-fd4fBlcAvxPD7I&forcekml=1 |
| CA | [Oceanside Turkey Trot](https://www.sandiegorunningco.com/sdrc_events/oside-turkey-trot/) | 5K | unsupported | only googlemaps, image, mapmyrun |
| CA | [Rock 'n' Roll San Diego](https://www.runrocknroll.com/events/san-diego/course-overview) | Half Marathon | unsupported | only image, pdf |
| CA | [Rock 'n' Roll San Diego](https://www.runrocknroll.com/events/san-diego/course-overview) | Marathon | unsupported | only image, pdf |
| CA | [Rose Bowl Half Marathon](https://www.mccourtfoundation.org/event/rose-bowl-half-5k/course/) | Half Marathon | unsupported | only image, pdf |
| CA | [Run to Feed the Hungry](https://www.runtofeedthehungry.com/racedayinfo) | 10K | unsupported | only pdf |
| CA | [Run to Feed the Hungry](https://www.runtofeedthehungry.com/racedayinfo) | 5K | unsupported | only pdf |
| CA | [The San Francisco Marathon](https://www.thesfmarathon.com/10k/) | 10K | unsupported | only googlemaps, image |
| CA | [The San Francisco Marathon](https://www.thesfmarathon.com/1st-half-marathon/) | 1st Half Marathon (Bridge Half) | unsupported | only googlemaps, image, pdf |
| CA | [The San Francisco Marathon](https://www.thesfmarathon.com/2nd-half-marathon/) | 2nd Half Marathon (City Half) | unsupported | only googlemaps, image |
| CA | [The San Francisco Marathon](https://www.thesfmarathon.com/full-marathon/) | Marathon | unsupported | only googlemaps, image |
| CA | [The San Francisco Marathon](https://www.thesfmarathon.com/5k-races-overview/) | Saturday 5K | unsupported | only googlemaps, image, pdf |
| CA | [The San Francisco Marathon](https://www.thesfmarathon.com/5k-races-overview/) | Sunday 5K | unsupported | only googlemaps, image, pdf |
| CA | [Shamrock'n Half Marathon](https://shamrocknhalf.com/runner-information/) | 10K | unsupported | only image, pdf |
| CA | [Shamrock'n Half Marathon](https://shamrocknhalf.com/runner-information/) | 5K | unsupported | only image, pdf |
| CA | [Shamrock'n Half Marathon](https://shamrocknhalf.com/runner-information/) | Half Marathon | unsupported | only image, pdf |
| CA | [Applied Materials Silicon Valley Turkey Trot](https://www.svturkeytrot.com/course-map/) | 10K | unsupported | only image |
| CA | [Applied Materials Silicon Valley Turkey Trot](https://www.svturkeytrot.com/course-map/) | 5K | unsupported | only image |
| CA | [Silver Strand Half Marathon](https://www.silverstrandhalf.com/course-map) | Half Marathon | unsupported | only image, ridewithgps |
| CA | [Surf City Marathon](https://www.runsurfcity.com/halfmarathon) | Half Marathon | unsupported | only image, pdf |
| CA | [Two Cities Marathon & Half](https://www.run2cm.com/courses) | Half Marathon | unsupported | only strava |
| CA | [Urban Cow Half Marathon](https://urbancowhalf.com/event-information/course-information/) | 5K | unsupported | only image, pdf |
| CA | [Urban Cow Half Marathon](https://urbancowhalf.com/event-information/course-information/) | Half Marathon | unsupported | only image, pdf |
| CA | [Santa Cruz to Capitola Wharf to Wharf Race](https://wharftowharf.com/wharf-to-wharf-race/) | 6 Mile | no-source | no course map on https://wharftowharf.com/, https://wharftowharf.com/wharf-to-wharf-race/ |
| CO | [Denver Colfax Marathon](https://www.runcolfax.org/races/marathon-course-overview/) | Marathon | unsupported | only image |
| CO | [Colorado Marathon](https://comarathon.com/full-marathon) | Marathon | unsupported | only googlemaps, image |
| CO | [Mile High United Way Turkey Trot](https://www.unitedwaydenver.org/turkeytrot) | 4 Mile | unsupported | only googlemaps, plotaroute |
| CT | [Athletic Brewing Company Fairfield Road Races](https://www.fairfieldhalf.space/course-maps) | Half Marathon | unsupported | only image |
| CT | [Eversource Hartford Marathon](https://www.hartfordmarathon.com/eversource-hartford-marathon/) | Half Marathon | unsupported | only pdf |
| CT | [Eversource Hartford Marathon](https://www.hartfordmarathon.com/eversource-hartford-marathon/) | Marathon | unsupported | only pdf |
| CT | [Lenny and Joe's Madison Turkey Trot](https://runsignup.com/Race/CT/Madison/LennyandJoesMadisonTurkeyTrot) | 5 Miles | unsupported | only image, pdf |
| CT | [Manchester Road Race](https://www.manchesterroadrace.com/page/race-information-and-rules) | Manchester Road Race | unsupported | only googlemaps |
| CT | [Faxon Law New Haven Road Race](https://www.newhavenroadrace.org/course-maps) | Half Marathon | unsupported | only image, pdf |
| CT | [Newtown Turkey Trot](https://runsignup.com/Race/CT/Newtown/NewtownTurkeyTrot) | 5K | unsupported | only image |
| CT | [Rowayton Turkey Trot](https://www.rowaytonturkeytrot.com/) | 5K | unsupported | only googlemaps |
| DC | [Credit Union Cherry Blossom Ten Mile Run](https://cherryblossom.org/pre-race/resources/maps/) | 10 Mile | unsupported | only image, pdf |
| DC | [Credit Union Cherry Blossom Ten Mile Run](https://cherryblossom.org/pre-race/resources/maps/) | 5K | unsupported | only image, pdf |
| DC | [St. Jude Rock 'n' Roll Washington DC](https://www.runrocknroll.com/events/washington-dc/course-overview) | 5K | unsupported | only image, pdf |
| DC | [St. Jude Rock 'n' Roll Washington DC](https://www.runrocknroll.com/events/washington-dc/course-overview) | Half Marathon | unsupported | only image, pdf |
| DC | [SOME's Trot for Hunger](https://runsignup.com/Race/DC/Washington/americastrotforhunger) | 5K | unsupported | only googlemaps, image |
| FL | [Coffee Pot Turkey Trot](https://runsignup.com/Race/FL/SaintPetersburg/NorthShoreElementarySchoolCoffeePotTurkeyTrot) | 5K | no-match | no line near 5.00 km in https://www.google.com/maps/d/kml?mid=1ThLmQvY4JH7sTSYznopKDn4jr3axctll&forcekml=1 |
| FL | [Disney Princess Half Marathon Weekend](https://www.rundisney.com/events/disneyworld/disney-princess-half-marathon-weekend/) | 10K | error | HTTP 403: https://www.rundisney.com/events/disneyworld/disney-princess-half-marathon-weekend/ |
| FL | [Disney Princess Half Marathon Weekend](https://www.rundisney.com/events/disneyworld/disney-princess-half-marathon-weekend/) | Half Marathon | error | HTTP 403: https://www.rundisney.com/events/disneyworld/disney-princess-half-marathon-weekend/ |
| FL | [runDisney Springtime Surprise Weekend](https://www.rundisney.com/events/disneyworld/springtime-surprise-weekend/) | 10 Miler | error | HTTP 403: https://www.rundisney.com/events/disneyworld/springtime-surprise-weekend/ |
| FL | [runDisney Springtime Surprise Weekend](https://www.rundisney.com/events/disneyworld/springtime-surprise-weekend/) | 10K | error | HTTP 403: https://www.rundisney.com/events/disneyworld/springtime-surprise-weekend/ |
| FL | [Disney Wine & Dine Half Marathon Weekend](https://www.rundisney.com/events/disneyworld/disney-wine-and-dine-half-marathon-weekend/) | 10K | error | HTTP 403: https://www.rundisney.com/events/disneyworld/disney-wine-and-dine-half-marathon-weekend/ |
| FL | [Disney Wine & Dine Half Marathon Weekend](https://www.rundisney.com/events/disneyworld/disney-wine-and-dine-half-marathon-weekend/) | Half Marathon | error | HTTP 403: https://www.rundisney.com/events/disneyworld/disney-wine-and-dine-half-marathon-weekend/ |
| FL | [Fort Myers Turkey Trot 5K](https://runsignup.com/Race/FL/FortMyers/FMTCTurkeyTrot5K) | 5K | unsupported | only googlemaps, image, mapmyrun |
| FL | [Publix Gasparilla Distance Classic](https://www.rungasparilla.com/15k-course-information/) | 15K | unsupported | only image, pdf |
| FL | [Publix Gasparilla Distance Classic](https://www.rungasparilla.com/5k-course-information/) | 5K | unsupported | only image, pdf |
| FL | [Publix Gasparilla Distance Classic](https://www.rungasparilla.com/8k-course-information/) | 8K | unsupported | only image, pdf |
| FL | [Publix Gasparilla Distance Classic](https://www.rungasparilla.com/half-marathon-course-information/) | Half Marathon | unsupported | only image, pdf |
| FL | [Gate River Run](https://gateriverrun15k.com/15k/) | 15K | unsupported | only image, plotaroute |
| FL | [Gate River Run](https://gateriverrun15k.com/15k/) | 5K | unsupported | only image, plotaroute |
| FL | [Key West Half Marathon & Runfest](https://www.keywesthalfmarathon.com/event-details/course-maps/) | 10K | unsupported | only image, pdf |
| FL | [Key West Half Marathon & Runfest](https://www.keywesthalfmarathon.com/event-details/course-maps/) | 5K | unsupported | only image, pdf |
| FL | [Key West Half Marathon & Runfest](https://www.keywesthalfmarathon.com/event-details/course-maps/) | Half Marathon | unsupported | only image, pdf |
| FL | [Lexus Corporate Run Miami](https://lexuscorporaterun.com/assets/printable/mia_course-map.pdf) | 5K | unsupported | only googlemaps, pdf |
| FL | [Life Time Miami Marathon and Half](https://www.themiamimarathon.com/half-marathon-course/) | Half Marathon | unsupported | only garmin, image, pdf |
| FL | [Life Time Miami Marathon and Half](https://www.themiamimarathon.com/marathon-course/) | Marathon | unsupported | only garmin, image, pdf |
| FL | [Life Time Miami Marathon and Half](https://www.themiamimarathon.com/tropical-5k/) | Tropical 5K | unsupported | only image |
| FL | [Mount Dora Half Marathon & 5K](https://runsignup.com/Race/MountDoraHalfMarathon5K/Page/CourseRoute) | 5K | unsupported | only pdf |
| FL | [Mount Dora Half Marathon & 5K](https://runsignup.com/Race/MountDoraHalfMarathon5K/Page/CourseRoute) | Half Marathon | unsupported | only pdf |
| FL | [GCR Thanksgiving 5K](https://runsignup.com/Race/FL/Naples/2013GCRTurkeyTrot5K) | 5K | unsupported | only googlemaps, image |
| FL | [Barron Collier Companies Naples Half Marathon](https://napleshalfmarathon.net/travel/) | Half Marathon | unsupported | only googlemaps, image |
| FL | [Space Coast Marathon & Half Marathon](https://spacecoastmarathon.com/) | Half Marathon | unsupported | only image |
| FL | [Space Coast Turkey Trot 5K](https://runsignup.com/Race/FL/Melbourne/SpaceCoastTurkeyTrot5K10K) | 5K | unsupported | only googlemaps, image |
| FL | [Tampa YMCA Turkey Gobble 5K](https://runsignup.com/Race/TampaYMCATurkeyGobble/Page/Course-Map) | 5K | unsupported | only image |
| FL | [Trot Against Poverty 5K](https://www.trotagainstpoverty.org/) | 5K | unsupported | only image |
| FL | [Walt Disney World Marathon Weekend](https://www.rundisney.com/events/disneyworld/disney-world-marathon-weekend/) | 10K | error | HTTP 403: https://www.rundisney.com/events/disneyworld/disney-world-marathon-weekend/ |
| FL | [Walt Disney World Marathon Weekend](https://www.rundisney.com/events/disneyworld/disney-world-marathon-weekend/) | Half Marathon | error | HTTP 403: https://www.rundisney.com/events/disneyworld/disney-world-marathon-weekend/ |
| FL | [Walt Disney World Marathon Weekend](https://www.rundisney.com/events/disneyworld/disney-world-marathon-weekend/) | Marathon | error | HTTP 403: https://www.rundisney.com/events/disneyworld/disney-world-marathon-weekend/ |
| GA | [AthHalf Half Marathon](https://athhalf.com/athhalf/) | Half Marathon | unsupported | only image, pdf |
| GA | [Northside Hospital Peachtree Road Race](https://www.atlantatrackclub.org/course) | 10K | unsupported | only garmin, pdf |
| GA | [Running of the Turkeys 5K](https://runsignup.com/Race/GA/Roswell/runningoftheturkeysga) | 5K | unsupported | only image |
| GA | [Enmarket Savannah Bridge Run](https://runsignup.com/Race/GA/Savannah/SAVBridgeRun) | 5K | unsupported | only googlemaps, image |
| HI | [The Hapalua - Hawaii's Half Marathon](https://www.thehapalua.com/key-information/course-description) | Half Marathon | unsupported | only image, pdf, strava |
| HI | [JAL Honolulu Marathon](https://www.honolulumarathon.org/our-events/kalakaua-merrie-mile) | Kalakaua Merrie Mile | unsupported | only garmin, image, pdf |
| HI | [JAL Honolulu Marathon](https://www.honolulumarathon.org/key-information/course-description) | Marathon | unsupported | only garmin, image, pdf |
| HI | [JAL Honolulu Marathon](https://www.honolulumarathon.org/our-events/start-to-park-10k) | Start to Park 10K | unsupported | only garmin, image, pdf |
| HI | [The Kauai Marathon & Half Marathon](https://thekauaimarathon.com/the-race/the-course/) | Half Marathon | unsupported | only image, mapmyrun |
| IA | [Quad-City Times Bix 7](https://bix7.com/course-map/) | Bix 7 | unsupported | only image |
| IL | [Bank of America Chicago 13.1](https://www.chicago13point1.com/event-information/participant-information/course/) | Half Marathon | unsupported | only image, pdf |
| IL | [Life Time Chicago Half Marathon](https://www.chicagohalfmarathon.com/half-marathon/) | Half Marathon | unsupported | only pdf |
| IL | [Bank of America Chicago Marathon](https://www.chicago5k.com/event-information/) | Abbott Chicago 5K | unsupported | only pdf |
| IL | [Bank of America Chicago Marathon](https://www.chicagomarathon.com/course/) | Marathon | unsupported | only image, pdf |
| IL | [JPMorganChase Corporate Challenge Chicago](https://www.jpmorganchasecc.com/en/home/our-locations/chicago/the-event) | 3.5 Mile | unsupported | only image, pdf |
| IL | [Christie Clinic Illinois Marathon](https://illinoismarathon.com/course-info/) | 10K | unsupported | only image, pdf |
| IL | [Christie Clinic Illinois Marathon](https://illinoismarathon.com/course-info/) | 5K | unsupported | only image, pdf |
| IL | [Christie Clinic Illinois Marathon](https://illinoismarathon.com/course-info/) | Half Marathon | unsupported | only image, pdf |
| IL | [Bank of America Shamrock Shuffle](https://www.shamrockshuffle.com/shufflers/course/) | 8K | unsupported | only image, pdf |
| IN | [Wheeler Mission Drumstick Dash](https://runsignup.com/Race/DrumstickDashIndy/Page/Course-Map) | 2.6 Mile Mini Gobbler | no-source | no course map on https://runsignup.com/Race/DrumstickDashIndy/Page/Course-Map, https://www.drumstickdash.org/, https://www.drumstickdash.org/Race/DrumstickDashIndy/Page/Corral-Map, https://www.drumstickdash.org/Race/DrumstickDashIndy/Page/Course-Entertainment, https://www.drumstickdash.org/Race/DrumstickDashIndy/Page/Course-Map |
| IN | [Wheeler Mission Drumstick Dash](https://runsignup.com/Race/DrumstickDashIndy/Page/Course-Map) | 4.3 Mile Full Gobbler | no-source | no course map on https://runsignup.com/Race/DrumstickDashIndy/Page/Course-Map, https://www.drumstickdash.org/, https://www.drumstickdash.org/Race/DrumstickDashIndy/Page/Corral-Map, https://www.drumstickdash.org/Race/DrumstickDashIndy/Page/Course-Entertainment, https://www.drumstickdash.org/Race/DrumstickDashIndy/Page/Course-Map |
| IN | [Fort4Fitness Fall Festival](https://www.fort4fitness.org/fall-festival/4-mile-walk-run) | 4 Mile | no-match | no line near 6.44 km in https://www.google.com/maps/d/kml?mid=1YHh2zMA59-VYhTYIt5hMootOF1dyGP0&forcekml=1 |
| IN | [CNO Financial Indianapolis Monumental Marathon](https://monumentalmarathon.com/races/cno-financial-indianapolis-monumental-marathon/) | Marathon | unsupported | only pdf |
| IN | [IU Health 500 Festival Mini-Marathon](https://www.indymini.com/p/mini-marathon/participantinfo/maps) | Half Marathon | unsupported | only image, pdf |
| KS | [Garmin Olathe Marathon](https://ozrun.org/course-maps/) | Half Marathon | unsupported | only image |
| KS | [Prairie Fire Fall Marathon](https://wichitasports.com/events/prairie-fire-race-series/) | Half Marathon | error | HTTP 403: https://wichitasports.com/events/prairie-fire-race-series/ |
| KY | [Kentucky Derby Festival miniMarathon & Marathon](https://derbyfestivalmarathon.com/course-details/) | Marathon | unsupported | only image, pdf |
| KY | [Kentucky Derby Festival miniMarathon & Marathon](https://derbyfestivalmarathon.com/course-details/) | miniMarathon | unsupported | only image, pdf |
| KY | [Northeast Family YMCA Thanksgiving Turkey Trot](https://runsignup.com/Race/KY/Louisville/TurkeyDayFun) | 5K | no-source | no course map on https://runsignup.com/Race/KY/Louisville/TurkeyDayFun |
| KY | [Urban Bourbon Half Marathon](https://www.urbanbourbonhalf.com/Race/UrbanBourbonHalfMarathon/Page/COURSES) | Half Marathon | unsupported | only image |
| LA | [Crescent City Classic](https://ccc10k.com/ccc10k/) | 10K | unsupported | only image |
| LA | [The Louisiana Marathon](https://thelouisianamarathon.com/Race/TheLouisianaMarathon/Page/QuarterMarathon5K) | 5K | unsupported | only image, pdf, plotaroute |
| LA | [The Louisiana Marathon](https://thelouisianamarathon.com/Race/TheLouisianaMarathon/Page/SundayRaceCourses) | Half Marathon | unsupported | only image, pdf, plotaroute |
| LA | [The Louisiana Marathon](https://thelouisianamarathon.com/Race/TheLouisianaMarathon/Page/SundayRaceCourses) | Marathon | unsupported | only image, pdf, plotaroute |
| MA | [Baystate Marathon](https://www.baystatemarathon.com/course-map-description) | Marathon | unsupported | only garmin, image |
| MA | [Boston 10K](https://www.baa.org/races/boston-10k/) | 10K | reject | length 8.78 km is -12.2% off target; joined from 75 of 78 pieces of the map |
| MA | [Boston Marathon](https://www.baa.org/races/boston-5k/) | Boston 5K | unsupported | only image |
| MA | [Boston's Run to Remember](https://www.bostonsruntoremember.org/course-info) | 5 Miler | unsupported | only garmin, image, mapmyrun, pdf |
| MA | [Boston's Run to Remember](https://www.bostonsruntoremember.org/course-info) | Half Marathon | unsupported | only garmin, image, mapmyrun, pdf |
| MA | [Cambridge Half Marathon](https://runsignup.com/Race/CambridgeHalfMarathon/Page/Course-Map) | Half Marathon | unsupported | only googlemaps, image |
| MA | [Harborside Half Marathon & 5K](https://harborsidehalf.com/race-details/) | Half Marathon | unsupported | only googlemaps, image, pdf, strava |
| MA | [Harpoon 5-Miler](https://runsignup.com/Race/MA/Boston/Harpoon5Miler) | 5 Miles | no-source | no course map on https://runsignup.com/Race/Harpoon5Miler/Page/Course-Safety-On-Course, https://runsignup.com/Race/MA/Boston/Harpoon5Miler |
| MA | [Hingham Turkey Trot](https://www.hinghamturkeytrot.com/) | 5K | unsupported | only googlemaps, pdf |
| MA | [New Bedford Half Marathon](https://millenniumrunning.com/newbedfordhalfmarathon/) | Half Marathon | unsupported | only garmin, googlemaps, image |
| MA | [Newton Turkey Trot](https://runsignup.com/Race/NewtonTurkeyTrot/Page/RaceandCourseInformation) | 5K | unsupported | only googlemaps, image |
| MA | [Gobble Gobble Gobble](https://www.srr.org/gobble) | 4 Miler | unsupported | only googlemaps, image |
| MA | [Wellesley Turkey Trot](https://runsignup.com/Race/MA/Wellesley/WellesleyTurkeyTrot) | 5K | unsupported | only image |
| MD | [Baltimore 10 Miler](http://www.baltimoretenmiler.com/Race/BALTIMORE10MILER/Page/CourseDetails) | 10 Mile | unsupported | only googlemaps, image, plotaroute |
| MD | [Baltimore Running Festival](https://www.thebaltimoremarathon.com/Race/TheBaltimoreRunningFestival/Page/10K) | 10K | unsupported | only googlemaps, image, plotaroute |
| MD | [Baltimore Running Festival](https://www.thebaltimoremarathon.com/Race/TheBaltimoreRunningFestival/Page/5K) | 5K | unsupported | only image, plotaroute |
| MD | [Baltimore Running Festival](https://www.thebaltimoremarathon.com/Race/TheBaltimoreRunningFestival/Page/HalfMarathon) | Half Marathon | unsupported | only image, plotaroute |
| MD | [Baltimore Running Festival](https://www.thebaltimoremarathon.com/Race/TheBaltimoreRunningFestival/Page/Marathon) | Marathon | unsupported | only image, plotaroute |
| MD | [Bay Bridge Run](https://runsignup.com/Race/BayBridgeRun/Page/TheCourse) | 10K | unsupported | only image |
| MD | [YMCA Turkey Chase Charity Race](https://runsignup.com/Race/YMCATurkeyChase/Page/Maps) | 10K | unsupported | only image |
| ME | [TD Beach to Beacon 10K](https://www.beach2beacon.org/race-weekend/10k-race-info/) | 10K | unsupported | only image |
| ME | [Maine Coast Marathon](https://www.mainecoastmarathon.com/) | Half Marathon | no-source | no course map on https://www.mainecoastmarathon.com/ |
| ME | [Maine Marathon](https://mainemarathon.com/races/half-marathon/) | Half Marathon | unsupported | only image, mapmyrun, pdf |
| ME | [Maine Marathon](https://mainemarathon.com/races/marathon/) | Marathon | unsupported | only image, mapmyrun, pdf |
| ME | [Millinocket Marathon & Half](https://www.crowathletics.com/millinocket-race-overview) | Half Marathon | unsupported | only googlemaps, mapmyrun |
| ME | [Portland Sea Dogs Mother's Day 5K](https://www.milb.com/portland/community/mothersday5k) | 5K | no-source | no course map on https://www.milb.com/portland/community/mothersday5k |
| MI | [Bayshore Marathon](https://www.bayshoremarathon.org/course-information) | 10K | unsupported | only image |
| MI | [Bayshore Marathon](https://www.bayshoremarathon.org/course-information) | Half Marathon | unsupported | only image |
| MI | [Bayshore Marathon](https://www.bayshoremarathon.org/course-information) | Marathon | unsupported | only image |
| MI | [Big House 5K](https://runsignup.com/Race/BigHouse5K/Page/Course-Maps) | 5K | unsupported | only pdf |
| MI | [Strategic Staffing Solutions Turkey Trot](https://theparade.org/turkeytrot/general-info/course-maps/) | 10K Turkey Trot | unsupported | only image, pdf |
| MI | [Strategic Staffing Solutions Turkey Trot](https://theparade.org/turkeytrot/general-info/course-maps/) | 5K Stuffing Strut | unsupported | only image, pdf |
| MI | [Grand Rapids Marathon](https://www.grandrapidsmarathon.com/information/course-maps/) | Half Marathon | unsupported | only image, pdf |
| MI | [Grand Rapids Marathon](https://www.grandrapidsmarathon.com/information/course-maps/) | Marathon | unsupported | only image, pdf |
| MI | [Amway River Bank Run](https://amwayriverbankrun.com/course/) | 10K | unsupported | only pdf |
| MI | [Amway River Bank Run](https://amwayriverbankrun.com/course/) | 25K | unsupported | only pdf |
| MI | [Amway River Bank Run](https://amwayriverbankrun.com/course/) | 5K | unsupported | only pdf |
| MN | [Get in Gear](https://www.tcmevents.org/alleventsandraces/getingear) | 10K | unsupported | only image, pdf |
| MN | [Get in Gear](https://www.tcmevents.org/alleventsandraces/getingear) | 5K | unsupported | only image, pdf |
| MN | [Get in Gear](https://www.tcmevents.org/alleventsandraces/getingear) | Half Marathon | unsupported | only image, pdf |
| MN | [Goldy's Run](https://www.goldysrun.com/5k) | 5K | unsupported | only image, mapmyrun |
| MN | [Grandma's Marathon](https://grandmasmarathon.com/the-marathon/garry-bjorklund-half-marathon/) | Garry Bjorklund Half Marathon | unsupported | only image, pdf |
| MN | [Grandma's Marathon](https://grandmasmarathon.com/the-marathon/grandmas-marathon/) | Marathon | unsupported | only image, pdf |
| MN | [Grandma's Marathon](https://grandmasmarathon.com/the-marathon/william-a-irvin-5k/) | William A. Irvin 5K | unsupported | only image, pdf |
| MN | [Milk Run](https://www.mnstatefair.org/kickoff-to-summer/milk-run) | 5K | unsupported | only image, pdf |
| MN | [Turkey Day 5K](https://www.tcmevents.org/alleventsandraces/turkeyday/turkeyday5k) | 5K | unsupported | only googlemaps, image, pdf |
| MN | [North Start (formerly Hot Dash)](https://www.tcmevents.org/alleventsandraces/hotdash) | 5K | no-source | no course map on https://www.tcmevents.org/alleventsandraces/hotdash |
| MN | [Stars and Strides Minneapolis](https://www.minnesotarunningseries.com/starsandstridesminneapolis) | 5K | unsupported | only image |
| MN | [Tonka Turkey Trot](https://www.minnetonkaschools.org/district/partners/booster/turkey-trot/map) | 5K | unsupported | only mapmyrun |
| MN | [Turkey Trot St. Paul](https://www.minnesotarunningseries.com/turkey-trot-st-paul) | 10K | unsupported | only image |
| MN | [Medtronic Twin Cities Marathon](https://www.tcmevents.org/alleventsandraces/medtronictwincitiesmarathonweekend/medtronictwincitiesmarathon) | Marathon | unsupported | only image, pdf |
| MN | [Medtronic Twin Cities Marathon](https://www.tcmevents.org/alleventsandraces/medtronictwincitiesmarathonweekend/tc10mile) | TC 10 Mile | unsupported | only googlemaps, image, pdf |
| MN | [Medtronic Twin Cities Marathon](https://www.tcmevents.org/alleventsandraces/medtronictwincitiesmarathonweekend/tc10k) | TC 10K | unsupported | only image, pdf |
| MN | [PNC Women Run the Cities](https://www.tcmevents.org/alleventsandraces/pncwomenrunthecities) | 10K | unsupported | only image, pdf |
| MN | [PNC Women Run the Cities](https://www.tcmevents.org/alleventsandraces/pncwomenrunthecities) | 5K | unsupported | only image, pdf |
| MO | [Hospital Hill Run](https://www.sportkc.org/hospital-hill-course-maps) | 5K | unsupported | only garmin, googlemaps, image, pdf |
| MO | [Hospital Hill Run](https://www.sportkc.org/hospital-hill-course-maps) | Half Marathon | unsupported | only garmin, googlemaps, image, pdf |
| MO | [Garmin Kansas City Marathon](https://www.sportkc.org/marathon/course-maps) | 10K | unsupported | only image, pdf |
| MO | [Garmin Kansas City Marathon](https://www.sportkc.org/marathon/course-maps) | 5K | unsupported | only image, pdf |
| MO | [Garmin Kansas City Marathon](https://www.sportkc.org/marathon/course-maps) | Half Marathon | unsupported | only image, pdf |
| MO | [Garmin Kansas City Marathon](https://www.sportkc.org/marathon/course-maps) | Marathon | unsupported | only image, pdf |
| MO | [Rock the Parkway Half Marathon & 5K](https://www.rocktheparkway.com/race-information/course/) | 5K | unsupported | only image, pdf |
| MO | [Rock the Parkway Half Marathon & 5K](https://www.rocktheparkway.com/race-information/course/) | Half Marathon | unsupported | only image, pdf |
| MO | [Bass Pro Fitness Series Marathon Weekend](https://fitness.basspro.com/events/marathon-weekend-events.html) | CMC Recycling 5K | error | HTTP 403: https://fitness.basspro.com/events/marathon-weekend-events/cohick-half-marathon.html; HTTP 403: https://fitness.basspro.com/events/marathon-weekend-events.html; HTTP 403: https://fitness.basspro.com/events/marathon-weekend-events/fitness-series-5K.html |
| MO | [Bass Pro Fitness Series Marathon Weekend](https://fitness.basspro.com/events/marathon-weekend-events.html) | Cohick Half Marathon | error | HTTP 403: https://fitness.basspro.com/events/marathon-weekend-events/cohick-half-marathon.html; HTTP 403: https://fitness.basspro.com/events/marathon-weekend-events.html |
| MO | [Springfield Turkey Trot](https://www.parkboard.org/624/29th-Annual-Turkey-Trot) | 5K | no-match | no line near 5.00 km in https://www.google.com/maps/d/kml?mid=1GWi3uqBrcGQqN_iYWg4igElBk16fJnCe&forcekml=1 |
| MO | [St. Louis Marathon](https://gostlouis.org/races/st-louis-marathon/) | Marathon | no-match | no line near 42.20 km in https://www.google.com/maps/d/kml?mid=1Vn1r2UJrlivy8db4OyK6KbWjNCfvw_A&forcekml=1; no line near 42.20 km in https://www.google.com/maps/d/kml?mid=1Vn1r2UJrlivy8db4OyK6KbWjNCfvw_A&forcekml=1 |
| MO | [CCVI Trolley Run](https://www.trolleyrun.org/) | 4 Mile | no-source | no course map on https://www.trolleyrun.org/ |
| MS | [Keesler Federal Mississippi Gulf Coast Marathon](https://runsignup.com/Race/MSGulfCoastMarathon/Page/5-K) | 5K | unsupported | only image, plotaroute |
| MS | [Keesler Federal Mississippi Gulf Coast Marathon](https://runsignup.com/Race/MSGulfCoastMarathon/Page/SundayRaceCourses) | Half Marathon | unsupported | only image, plotaroute |
| MT | [Missoula Marathon](https://www.missoulamarathon.org/events/marathon/) | Marathon | unsupported | only image |
| NC | [Novant Health Charlotte Marathon](https://charlottesports.org/event/charlotte-marathon/runner-info/) | 5K | unsupported | only image, mapmyrun |
| NC | [Novant Health Charlotte Marathon](https://charlottesports.org/event/charlotte-marathon/runner-info/) | Half Marathon | unsupported | only image, mapmyrun |
| NC | [Novant Health Charlotte Marathon](https://charlottesports.org/event/charlotte-marathon/runner-info/) | Marathon | unsupported | only image, mapmyrun |
| NC | [CPI Security Charlotte Turkey Trot](https://www.cltturkeytrot.com/course-details) | 5K | no-source | no course map on https://www.cltturkeytrot.com/, https://www.cltturkeytrot.com/course-details |
| NC | [CPI Security Charlotte Turkey Trot](https://www.cltturkeytrot.com/course-details) | 8K | no-source | no course map on https://www.cltturkeytrot.com/, https://www.cltturkeytrot.com/course-details |
| NC | [Trophy Trot 5K](https://event.racereach.com/trophy-trot/) | 5K | unsupported | only googlemaps, image |
| NC | [Novant Health Wilmington Marathon](https://wilmingtonncmarathon.com/half-marathon/) | Half Marathon | unsupported | only pdf |
| NC | [Novant Health Wilmington Marathon](https://wilmingtonncmarathon.com/full-marathon/) | Marathon | unsupported | only pdf |
| NC | [Turkey Strut 5K](https://runsignup.com/Race/NC/WinstonSalem/JRCTurkeyStrut5K) | 5K | unsupported | only image, pdf |
| ND | [Essentia Health Fargo Marathon](https://fargomarathon.com/) | 10K | no-source | no course map on https://fargomarathon.com/ |
| ND | [Essentia Health Fargo Marathon](https://fargomarathon.com/) | 5K | no-source | no course map on https://fargomarathon.com/ |
| ND | [Essentia Health Fargo Marathon](https://fargomarathon.com/) | Half Marathon | no-source | no course map on https://fargomarathon.com/ |
| ND | [Essentia Health Fargo Marathon](https://fargomarathon.com/) | Marathon | no-source | no course map on https://fargomarathon.com/ |
| NE | [Lincoln Marathon](https://www.lincolnmarathon.org/details/) | Half Marathon | unsupported | only image |
| NE | [Lincoln Marathon](https://www.lincolnmarathon.org/details/) | Marathon | unsupported | only image |
| NE | [YMCA of Lincoln Turkey Trot](https://www.ymcalincoln.org/events/ymca-lincoln-turkey-trot) | 5K | no-source | no course map on https://www.ymcalincoln.org/events/ymca-lincoln-turkey-trot |
| NJ | [Atlantic City Marathon](https://www.acraceseries.com/course) | Half Marathon | unsupported | only image, pdf |
| NJ | [Belmar Five Mile Run](https://runsignup.com/Race/BelmarFiveMileRun/Page-33) | 5 Mile | unsupported | only image, mapmyrun |
| NJ | [Jersey City Marathon](https://www.jerseycitymarathon.com/) | Half Marathon | unsupported | only googlemaps |
| NJ | [Jersey City Marathon](https://www.jerseycitymarathon.com/) | Marathon | unsupported | only googlemaps |
| NJ | [Mercer County Turkey Trot](https://www.mercercountyturkeytrot.com/course-map) | 5K | unsupported | only image, pdf |
| NJ | [Spring Lake Five Mile Run](https://www.springlake5.org/information-sheet) | 5 Mile | unsupported | only image, mapmyrun, pdf |
| NV | [Las Vegas Marathon](https://vegasmarathon.com/info?tab=course) | Marathon | unsupported | only googlemaps, image |
| NV | [Rock 'n' Roll Las Vegas](https://www.runrocknroll.com/events/las-vegas/course-overview) | Half Marathon | unsupported | only image, pdf |
| NY | [New Balance Bronx 10 Mile](https://webassets.nyrr.org/nyrrwebsiteassets/Bronx10M25_Map_072825_RD2.pdf) | 10 Mile | unsupported | only googlemaps, pdf |
| NY | [NYCRUNS Brooklyn Experience Half Marathon](https://nycruns.com/race/nycruns-brooklyn-experience-half-marathon) | Half Marathon | unsupported | only image, pdf |
| NY | [RBC Brooklyn Half](https://webassets.nyrr.org/nyrrwebsiteassets/RBCBKH26_MapCourse_inset_Neighborhoods_M4.pdf) | Half Marathon | unsupported | only pdf |
| NY | [Buffalo Marathon](https://www.thebuffalomarathon.com/athletes/course-maps/) | Half Marathon | unsupported | only image, pdf |
| NY | [Buffalo Marathon](https://www.thebuffalomarathon.com/athletes/course-maps/) | Marathon | unsupported | only image, pdf |
| NY | [YMCA Buffalo Niagara Turkey Trot](https://www.ymcabn.org/ymca-turkey-trot/runner-information) | 8K | unsupported | only googlemaps, image, pdf |
| NY | [JPMorganChase Corporate Challenge New York](https://www.jpmorganchasecc.com/en/home/our-locations/new-york-city) | 3.5 Mile | no-source | no course map on https://www.jpmorganchasecc.com/en/home/our-locations/new-york-city |
| NY | [New Balance 5th Avenue Mile](https://www.nyrr.org/races-and-events/2026/new-balance-5th-avenue-mile) | Road Mile | unsupported | only googlemaps |
| NY | [Flower City Half Marathon](https://www.flowercitychallenge.com/half/course) | Half Marathon | unsupported | only image, mapmyrun |
| NY | [Great Cow Harbor 10K](https://www.cowharborrace.com/) | 10K | no-source | no course map on https://www.cowharborrace.com/ |
| NY | [Liverpool Turkey Trot](https://www.liverpoolturkeytrot.com/race-courses) | 5K | unsupported | only pdf |
| NY | [Mountain Goat Run](https://www.mountaingoatrun.org/Race/MountainGoatRun/Page/Course-Info) | 10 Mile | unsupported | only googlemaps, image |
| NY | [TCS New York City Marathon](https://www.nyrr.org/tcsnycmarathon) | Abbott Dash to the Finish Line 5K | reject | length 5.47 km is +9.5% off target |
| NY | [Mastercard New York Mini 10K](https://www.nyrr.org/races-and-events/2026/mastercard-new-york-mini-10k-womens-race) | 10K | unsupported | only googlemaps |
| NY | [United Airlines NYC Half](https://www.nyrr.org/races-and-events/2026/united-airlines-nyc-half) | Half Marathon | unsupported | only googlemaps |
| NY | [Citizens Queens 10K](https://webassets.nyrr.org/nyrrwebsiteassets/CTZQNS26_MapCourse_051326_RD8.pdf) | 10K | unsupported | only googlemaps, pdf |
| NY | [Race to Deliver 4M to Benefit God's Love We Deliver](https://www.nyrr.org/races-and-events/2026/race-to-deliver-4m-to-benefit-gods-love-we-deliver) | 4 Mile | unsupported | only googlemaps |
| NY | [Fleet Feet Rochester Half Marathon](https://www.rochestermarathon.com/race-weekend/course-maps) | Half Marathon | unsupported | only image, mapmyrun |
| NY | [Run as One 4M Presented by JPMorgan Chase](https://webassets.nyrr.org/nyrrwebsiteassets/RunAsOne26_MapRun_031126_RD3%201.pdf) | 4 Mile | unsupported | only googlemaps, pdf |
| NY | [NYRR Staten Island Half](https://webassets.nyrr.org/nyrrwebsiteassets/SIH25_Map_092625_M2%201.pdf) | Half Marathon | unsupported | only googlemaps, pdf |
| NY | [Syracuse Half Marathon](https://www.syracusehalf.com/Race/SyracuseHalfMarathon/Page/CourseMap) | Half Marathon | unsupported | only googlemaps, image, onthegomap, pdf |
| NY | [Boilermaker Road Race](https://www.boilermaker.com/15k/) | 15K | unsupported | only image |
| NY | [Boilermaker Road Race](https://www.boilermaker.com/5k/) | 5K | unsupported | only image |
| NY | [Webster Turkey Trot](https://yellowjacketracing.com/races/webster-turkey-trot-55th-year) | 2.5 Mile | unsupported | only googlemaps, image, mapmyrun |
| NY | [Webster Turkey Trot](https://yellowjacketracing.com/races/webster-turkey-trot-55th-year) | 4.4 Mile | unsupported | only googlemaps, image, mapmyrun |
| NY | [Wineglass Marathon](https://www.wineglassmarathon.com/races/guthrie-wineglass-marathon/) | Marathon | unsupported | only image |
| OH | [Air Force Marathon](https://www.usafmarathon.com/course-maps/) | 10K | unsupported | only image, pdf |
| OH | [Air Force Marathon](https://www.usafmarathon.com/course-maps/) | 5K | unsupported | only image, pdf |
| OH | [Air Force Marathon](https://www.usafmarathon.com/course-maps/) | Half Marathon | unsupported | only image, pdf |
| OH | [Air Force Marathon](https://www.usafmarathon.com/course-maps/) | Marathon | unsupported | only image, pdf |
| OH | [FirstEnergy Akron Marathon, Half Marathon & Team Relay](https://akronmarathon.org/race-series/akron-marathon/) | Half Marathon | no-source | no course map on https://akronmarathon.org/race-series/akron-marathon/ |
| OH | [The Karen P Nakon Turkey Dash](https://runsignup.com/Race/OH/Avon/NFTurkeyDash) | 5K | unsupported | only image, pdf, ridewithgps |
| OH | [Bay Days 5 Miler](https://runsignup.com/Race/BayDays/Page/Course) | 5 Mile | unsupported | only googlemaps, image |
| OH | [Bockfest 5K](https://flyingpigmarathon.com/tql-beer-series/event/bockfest-5k) | 5K | no-match | no line near 5.00 km in https://www.google.com/maps/d/kml?mid=1gaQGU9ApEWwlynJzdobaq2Uy_AeIKMg&forcekml=1 |
| OH | [Americana Festival 5K](https://runsignup.com/Race/OH/Centerville/Americana5k) | 5K | unsupported | only mapmyrun |
| OH | [Chagrin Falls Booster Club 5K Turkey Trot](https://runsignup.com/Race/OH/ChagrinFalls/ChagrinBoostersTurkeyTrot5K) | 5K | unsupported | only googlemaps, image |
| OH | [Western & Southern Thanksgiving Day Race](https://thanksgivingdayrace.com/race/western-southern-10k/) | 10K | unsupported | only image |
| OH | [Western & Southern Thanksgiving Day Race](https://thanksgivingdayrace.com/race/tdr-5k/) | 5K | unsupported | only image |
| OH | [University Hospitals Cleveland Marathon](https://www.clevelandmarathon.com/races/10k.aspx) | 10K | unsupported | only image, pdf, ridewithgps |
| OH | [University Hospitals Cleveland Marathon](https://www.clevelandmarathon.com/races/5k.aspx) | 5K | unsupported | only image, pdf, ridewithgps |
| OH | [University Hospitals Cleveland Marathon](https://www.clevelandmarathon.com/races/half-marathon.aspx) | Half Marathon | unsupported | only image, pdf, ridewithgps |
| OH | [University Hospitals Cleveland Marathon](https://www.clevelandmarathon.com/races/marathon.aspx) | Marathon | unsupported | only image, pdf, ridewithgps |
| OH | [Columbus 10K](https://www.columbus10k.com/) | 10K | unsupported | only googlemaps, image |
| OH | [Nationwide Children's Hospital Columbus Marathon & 1/2 Marathon](https://www.columbusmarathon.com/1-2-marathon) | Half Marathon | unsupported | only image, pdf |
| OH | [Nationwide Children's Hospital Columbus Marathon & 1/2 Marathon](https://www.columbusmarathon.com/jesseowens5k) | Jesse Owens 5K | unsupported | only image |
| OH | [Nationwide Children's Hospital Columbus Marathon & 1/2 Marathon](https://www.columbusmarathon.com/marathon) | Marathon | unsupported | only image, pdf |
| OH | [Chase Columbus Turkey Trot](https://www.columbusturkeytrot.com/) | 5 Miler | error | HTTP 522: https://www.columbusturkeytrot.com/ |
| OH | [Dave's Turkey Chase 5K](https://runtoledo.com/turkey-chase-course-guide/) | 5K | unsupported | only image |
| OH | [Delaware Turkey Trot](https://runsignup.com/Race/OH/Delaware/DelawareTurkeyTrot) | 5K | unsupported | only googlemaps, image |
| OH | [Flying Pig Marathon Weekend](https://flyingpigmarathon.com/flying-pig-marathon-weekend/event/10k) | 10K | no-match | no line near 10.00 km in https://www.google.com/maps/d/kml?mid=1gaQGU9ApEWwlynJzdobaq2Uy_AeIKMg&forcekml=1 |
| OH | [Flying Pig Marathon Weekend](https://flyingpigmarathon.com/flying-pig-marathon-weekend/event/5k) | 5K | no-match | no line near 5.00 km in https://www.google.com/maps/d/kml?mid=1gaQGU9ApEWwlynJzdobaq2Uy_AeIKMg&forcekml=1 |
| OH | [Flying Pig Marathon Weekend](https://flyingpigmarathon.com/flying-pig-marathon-weekend/event/50-west-mile) | Fifty West Mile | no-match | no line near 1.61 km in https://www.google.com/maps/d/kml?mid=1gaQGU9ApEWwlynJzdobaq2Uy_AeIKMg&forcekml=1 |
| OH | [Flying Pig Marathon Weekend](https://flyingpigmarathon.com/flying-pig-marathon-weekend/event/half-marathon) | Half Marathon | no-match | no line near 21.10 km in https://www.google.com/maps/d/kml?mid=1gaQGU9ApEWwlynJzdobaq2Uy_AeIKMg&forcekml=1 |
| OH | [Flying Pig Marathon Weekend](https://flyingpigmarathon.com/flying-pig-marathon-weekend/event/flying-pig-marathon) | Marathon | no-match | no line near 42.20 km in https://www.google.com/maps/d/kml?mid=1gaQGU9ApEWwlynJzdobaq2Uy_AeIKMg&forcekml=1 |
| OH | [Mercy Health Glass City Marathon](https://glasscitymarathon.org/course-maps/) | Half Marathon | unsupported | only googlemaps, image, mapmyrun, pdf |
| OH | [Mercy Health Glass City Marathon](https://glasscitymarathon.org/course-maps/) | Marathon | unsupported | only googlemaps, image, mapmyrun, pdf |
| OH | [Mercy Health Glass City Marathon](https://glasscitymarathon.org/course-maps/) | Savage 5K | unsupported | only googlemaps, image, mapmyrun, pdf |
| OH | [Minster Oktoberfest Classic 10K](https://runsignup.com/Race/OH/Minster/MinsterOktoberfestClassic10k) | 10K | no-source | no course map on https://runsignup.com/Race/OH/Minster/MinsterOktoberfestClassic10k |
| OH | [Thanks For Giving 4 Miler](https://www.narun.org/details) | 4 Miler | unsupported | only image |
| OH | [North Canton YMCA July 4th Race](https://runsignup.com/Race/OH/NorthCanton/NorthCantonYMCAJulyThRace) | 2 Mile | unsupported | only image, pdf |
| OH | [OhioHealth Capital City Half & Quarter Marathon](https://capitalcityhalfmarathon.com/event-info/maps/) | Columbus Promise 5K | unsupported | only image, mapmyrun, pdf |
| OH | [OhioHealth Capital City Half & Quarter Marathon](https://capitalcityhalfmarathon.com/event-info/maps/) | Half Marathon | unsupported | only image, mapmyrun, pdf |
| OH | [OhioHealth Capital City Half & Quarter Marathon](https://capitalcityhalfmarathon.com/event-info/maps/) | Quarter Marathon | unsupported | only image, mapmyrun, pdf |
| OH | [The Ohio State 4 Miler](https://ohiostatefourmiler.com/event-info/course-map/) | 4 Miler | unsupported | only image, pdf |
| OH | [Perry Rotary Turkey Trot](https://runsignup.com/Race/OH/Canton/PerryRotaryTurkeyTrot) | 5K | no-source | no course map on https://runsignup.com/Race/OH/Canton/PerryRotaryTurkeyTrot |
| OH | [Powell Turkey Trot 4 Miler](https://www.powellturkeytrot.com/) | 4 Miler | no-source | no course map on https://www.powellturkeytrot.com/ |
| OH | [Queen Bee Half Marathon](https://flyingpigmarathon.com/queen-bee-half-marathon-weekend/event/queen-bee-4-miler) | 4-Miler | unsupported | only mapmyrun, pdf |
| OH | [Queen Bee Half Marathon](https://flyingpigmarathon.com/queen-bee-half-marathon-weekend/event/queen-bee-half-marathon) | Half Marathon | unsupported | only mapmyrun, pdf |
| OH | [Thanksgiving Wattle](https://runsignup.com/Race/OH/GroveCity/ThanksgivingWattle) | 5K | unsupported | only image |
| OH | [Susan G. Komen Northwest Ohio Race for the Cure](https://runsignup.com/Race/SUSANGKOMENNWORacefortheCure/Page/Course-Map) | 5K | unsupported | only googlemaps, image |
| OH | [Tuscarawas County YMCA Turkey Trot](https://runsignup.com/Race/OH/Dover/TuscarawasCountyYMCATurkeyTrot) | 5K | no-source | no course map on https://runsignup.com/Race/OH/Dover/TuscarawasCountyYMCATurkeyTrot |
| OK | [Oklahoma City Memorial Marathon](https://okcmarathon.com/event-information/course-maps/) | Half Marathon | unsupported | only image, pdf |
| OK | [Williams Route 66 Marathon](https://www.route66marathon.com/pages/maps) | 5K | unsupported | only image, pdf |
| OK | [Williams Route 66 Marathon](https://www.route66marathon.com/pages/maps) | Half Marathon | unsupported | only image, pdf |
| OK | [Williams Route 66 Marathon](https://www.route66marathon.com/pages/maps) | Marathon | unsupported | only image, pdf |
| OR | [OTC Butte to Butte](https://www.buttetobutte.com/courses) | 10K | unsupported | only mapmyrun, pdf |
| OR | [OTC Butte to Butte](https://www.buttetobutte.com/courses) | 5K | unsupported | only mapmyrun, pdf |
| OR | [Eugene Marathon](https://www.eugenemarathon.com/eugene-5k) | 5K | unsupported | only image, pdf |
| OR | [Portland Marathon](https://www.portlandmarathon.com/10k) | 10K | unsupported | only image |
| OR | [Portland Marathon](https://www.portlandmarathon.com/half-marathon) | Half Marathon | unsupported | only image |
| OR | [Portland Marathon](https://www.portlandmarathon.com/marathon) | Marathon | unsupported | only image |
| OR | [Shamrock Run Fest](https://www.shamrockrun.com/5k) | 5K | unsupported | only pdf |
| OR | [Shamrock Run Fest](https://www.shamrockrun.com/8k) | 8K | unsupported | only pdf |
| OR | [Shamrock Run Fest](https://www.shamrockrun.com/halfmarathon) | Half Marathon | unsupported | only pdf |
| PA | [Independence Blue Cross Broad Street Run](https://www.broadstreetrun.com/raceguide/) | 10 Mile | unsupported | only image |
| PA | [Philadelphia Marathon Weekend](https://www.philadelphiamarathon.com/races/8k-run/) | 8K | unsupported | only image, pdf |
| PA | [Philadelphia Marathon Weekend](https://www.philadelphiamarathon.com/races/half-marathon/) | Half Marathon | unsupported | only image, pdf |
| PA | [Philadelphia Marathon Weekend](https://www.philadelphiamarathon.com/races/marathon/) | Marathon | unsupported | only image, pdf |
| PA | [Richard S. Caliguiri City of Pittsburgh Great Race](https://www.rungreatrace.com/10K) | 10K | unsupported | only googlemaps, pdf |
| PA | [Richard S. Caliguiri City of Pittsburgh Great Race](https://www.rungreatrace.com/5K) | 5K | unsupported | only googlemaps, pdf |
| PA | [DICK'S Sporting Goods Pittsburgh Marathon](https://p3r.org/sites/page.json?slug=course-information&site=pittsburgh-marathon) | 5K | reject | length 4.56 km is -8.7% off target |
| PA | [DICK'S Sporting Goods Pittsburgh Marathon](https://p3r.org/sites/page.json?slug=course-information&site=pittsburgh-marathon) | Marathon | no-match | no line near 42.20 km in https://www.google.com/maps/d/kml?mid=1zNDVBDOG5pguR_iRjNkCqyzaJfOAKV4&forcekml=1 |
| PA | [YMCA of Greater Pittsburgh Turkey Trot](https://p3r.org/races/ymca-turkey-trot) | 5 Mile | unsupported | only pdf |
| PA | [YMCA of Greater Pittsburgh Turkey Trot](https://p3r.org/races/ymca-turkey-trot) | 5K | unsupported | only pdf |
| PA | [Rocky Run](https://rockyrun.com/info/) | 10 Mile | unsupported | only image |
| PA | [Rocky Run](https://rockyrun.com/info/) | 5K | unsupported | only image |
| PA | [Run for the Diamonds](https://www.runfordiamonds.com/course-map) | 9 Mile | unsupported | only image |
| RI | [Blessing of the Fleet Road Race](https://narragansettlionsclub.org/annual-events/blessing-of-the-fleet-celebration/) | 10 Miles | unsupported | only googlemaps, image |
| RI | [Amica Newport Marathon & Half Marathon](https://newportmarathon.com/course/) | Half Marathon | no-match | no line near 21.10 km in https://www.google.com/maps/d/kml?mid=1sXmgAP78aOeJw80CHCiNu1XTqMc&forcekml=1 |
| RI | [Newport Rhode Races](https://rhoderaces.com/events/newport/) | Half Marathon | no-match | no line near 21.10 km in https://www.google.com/maps/d/kml?mid=1Lbj7gxYNHmIzyMuCm3_orDmVESJru-k&forcekml=1; no line near 21.10 km in https://www.google.com/maps/d/kml?mid=1Lbj7gxYNHmIzyMuCm3_orDmVESJru-k&forcekml=1 |
| RI | [Brightstar Downtown 5K](https://runsignup.com/Race/IGTDowntown5K/Page-1) | 5K | unsupported | only image |
| RI | [Rhode Island Half Marathon & 5K](https://runsignup.com/Race/RIHalf5K/Page-2) | Half Marathon | unsupported | only image, mapmyrun |
| SC | [Turkey Day Run & Gobble Wobble 5K](https://www.turkeydayrun.com/race-details/) | 5K | unsupported | only image |
| SC | [Cooper River Bridge Run](https://bridgerun.com/maps-2/) | 10K | unsupported | only image, pdf |
| SC | [TreesUpstate Turkey Day Run](https://runsignup.com/Race/SC/Greenville/TreesGreenvilleTurkeyDay8k) | 5K Run & Walk | unsupported | only pdf, ridewithgps |
| SC | [TreesUpstate Turkey Day Run](https://runsignup.com/Race/SC/Greenville/TreesGreenvilleTurkeyDay8k) | 8K | unsupported | only pdf, ridewithgps |
| SC | [Kiawah Island Marathon](https://kiawahresort.com/recreation/kiawah-island-marathon/course/) | Half Marathon | unsupported | only image, pdf |
| SC | [Kiawah Island Marathon](https://kiawahresort.com/recreation/kiawah-island-marathon/course/) | Marathon | unsupported | only image, pdf |
| SC | [Myrtle Beach Marathon](https://mbmarathon.com/maps-elevevations/) | 5K | no-match | no line near 5.00 km in https://www.google.com/maps/d/kml?mid=15ZriaUQfoVwDKTJ26nqD9cjKvZkKHso&forcekml=1 |
| SD | [Sioux Falls Marathon](https://www.siouxfallsmarathon.com/half-marathon) | Half Marathon | unsupported | only image, mapmyrun |
| TN | [Hot to Trot 5K](https://runsignup.com/Race/TN/Knoxville/HottoTrot) | 5K | unsupported | only image |
| TN | [Covenant Health Knoxville Marathon](https://knoxvillemarathon.com/course-maps/) | 5K | unsupported | only image, pdf, strava |
| TN | [Covenant Health Knoxville Marathon](https://knoxvillemarathon.com/course-maps/) | Half Marathon | unsupported | only image, pdf, strava |
| TN | [Regal Knoxville Turkey Trot 5K](https://runsignup.com/Race/knoxvilleturkeytrot/Page/Course) | 5K | unsupported | only image |
| TN | [St. Jude Rock 'n' Roll Running Series Nashville](https://www.runrocknroll.com/events/nashville/course-overview) | 10K | unsupported | only image, pdf |
| TN | [St. Jude Rock 'n' Roll Running Series Nashville](https://www.runrocknroll.com/events/nashville/course-overview) | 5K | unsupported | only image, pdf |
| TN | [St. Jude Rock 'n' Roll Running Series Nashville](https://www.runrocknroll.com/events/nashville/course-overview) | Half Marathon | unsupported | only image, pdf |
| TN | [St. Jude Rock 'n' Roll Running Series Nashville](https://www.runrocknroll.com/events/nashville/course-overview) | Marathon | unsupported | only image, pdf |
| TX | [ThunderCloud Subs Turkey Trot](https://www.thundercloud.com/event-info/) | 5 Mile | unsupported | only googlemaps, image |
| TX | [Statesman Capitol 10K](https://www.cap10k.com/course-description-map/) | 10K | unsupported | only image, pdf |
| TX | [The Cowtown](https://cowtownmarathon.org/2026-saturday-maps/) | 10K | unsupported | only pdf |
| TX | [The Cowtown](https://cowtownmarathon.org/2026-saturday-maps/) | 5K | unsupported | only pdf |
| TX | [The Cowtown](https://cowtownmarathon.org/2026-sunday-map_course/) | Half Marathon | unsupported | only pdf |
| TX | [The Cowtown](https://cowtownmarathon.org/2026-sunday-map_course/) | Marathon | unsupported | only pdf |
| TX | [BMW Dallas Marathon](https://dallasmarathon.com/dallas-marathon-festival/events/sunday-events) | Half Marathon | unsupported | only googlemaps, image, pdf |
| TX | [BMW Dallas Marathon](https://dallasmarathon.com/dallas-marathon-festival/events/sunday-events) | Marathon | unsupported | only googlemaps, image, pdf |
| TX | [Chevron Houston Marathon](https://www.chevronhoustonmarathon.com/course/) | Half Marathon | unsupported | only pdf |
| TX | [Chevron Houston Marathon](https://www.chevronhoustonmarathon.com/course/) | Marathon | unsupported | only pdf |
| TX | [Katy YMCA Turkey Dash](https://runsignup.com/Race/TX/Katy/KatyYMCATurkeyDash) | 5K | unsupported | only googlemaps |
| TX | [San Antonio Food Bank Turkey Trot](https://safoodbank.org/turkey-trot/) | 5K | no-match | no line near 5.00 km in https://www.google.com/maps/d/kml?mid=1o6mNyqDU18n6nuqeUPpW4JEJRarTdR8&forcekml=1 |
| TX | [San Antonio Marathon](https://sanantoniomarathon.com/courses) | Half Marathon | unsupported | only image, pdf |
| TX | [San Antonio Marathon](https://sanantoniomarathon.com/courses) | Marathon | unsupported | only image, pdf |
| TX | [The Woodlands Marathon](https://www.thewoodlandsmarathon.com/course-maps) | Half Marathon | unsupported | only googlemaps, image, pdf |
| TX | [The Woodlands Marathon](https://www.thewoodlandsmarathon.com/course-maps) | Marathon | unsupported | only googlemaps, image, pdf |
| UT | [REVEL Big Cottonwood](https://results.laurelt.com/bcm/info?tab=course) | Marathon | unsupported | only googlemaps, image |
| UT | [Salt Lake City Marathon](https://runsignup.com/Race/saltlakecitymarathon/Page/Course-Maps) | Marathon | unsupported | only googlemaps, image, mapmyrun, pdf |
| UT | [St. George Marathon](https://www.sgcityutah.gov/activity/special_events/st._george_marathon/marathon_information.php) | Marathon | unsupported | only googlemaps, image, pdf |
| UT | [Utah Valley Marathon](https://www.utahvalleymarathon.com/utah-valley-marathon-info/utah-valley-marathon-map) | Marathon | no-source | no course map on https://www.utahvalleymarathon.com/, https://www.utahvalleymarathon.com/utah-10k-race-info/10k-in-utah-map, https://www.utahvalleymarathon.com/utah-valley-half-marathon/utah-half-marathon-map, https://www.utahvalleymarathon.com/utah-valley-marathon-info/utah-valley-marathon-map |
| VA | [Arlington Turkey Trot 5K](https://runsignup.com/Race/ArlingtonVATurkeyTrot5K/Page/Course-Map) | 5K | unsupported | only googlemaps, image |
| VA | [Army Ten-Miler](https://www.armytenmiler.com/live-race-info/course/) | 10 Mile | unsupported | only image |
| VA | [Getem Services Big Blue 5K](https://www.bigblue5k.com/big-blue-5k/) | 5K | unsupported | only image, pdf |
| VA | [Boar's Head Turkey Trot 5K](https://runsignup.com/Race/VA/Charlottesville/BoarsHeadTurkeyTrot) | 5K | unsupported | only googlemaps, image, pdf |
| VA | [Charlottesville Ten Miler](http://www.cvilletenmiler.com/course.html) | 10 Mile | unsupported | only mapmyrun |
| VA | [Crawlin' Crab Half Marathon](https://crawlincrabhalf.com/crawlin-crab-5k/) | 5K | unsupported | only image, pdf |
| VA | [Crawlin' Crab Half Marathon](https://crawlincrabhalf.com/crawlin-crab-half-marathon/) | Half Marathon | unsupported | only image, pdf |
| VA | [YMCA Turkey Trot (Fredericksburg)](https://runsignup.com/Race/AnnualYMCATurkeyTrotVA/Page/Course-Maps) | 5K | unsupported | only googlemaps, image, pdf |
| VA | [Marine Corps Marathon](https://www.marinemarathon.com/events/marine-corps-marathon) | Marathon | unsupported | only image, pdf |
| VA | [Ukrop's Monument Avenue 10K](https://www.sportsbackers.org/event/ukrops-monument-avenue-10k/10k-course/) | 10K | unsupported | only googlemaps, image, mapmyrun, pdf, ridewithgps |
| VA | [Chartway Norfolk Harbor Half Marathon Weekend](https://norfolkharborhalf.com/5k/) | 5K | unsupported | only image |
| VA | [Chartway Norfolk Harbor Half Marathon Weekend](https://norfolkharborhalf.com/half-marathon/) | Half Marathon | unsupported | only image, pdf |
| VA | [Allianz Richmond Marathon](https://www.richmondmarathon.org/race-weekend/course-information/8k-course/) | 8K | unsupported | only image, pdf, ridewithgps |
| VA | [Allianz Richmond Marathon](https://www.richmondmarathon.org/race-weekend/course-information/half-marathon-course/) | Half Marathon | unsupported | only image, pdf, ridewithgps |
| VA | [Allianz Richmond Marathon](https://www.richmondmarathon.org/race-weekend/course-information/marathon-course/) | Marathon | unsupported | only image, pdf, ridewithgps |
| VA | [Virginia Credit Union River City Half](https://www.sportsbackers.org/event/rivercityhalf/) | Half Marathon | unsupported | only googlemaps, image, mapmyrun, pdf, ridewithgps |
| VA | [Yuengling Shamrock Marathon Weekend](https://www.shamrockmarathon.com/8k/) | 8K | unsupported | only image |
| VA | [Yuengling Shamrock Marathon Weekend](https://www.shamrockmarathon.com/halfmarathon/) | Half Marathon | unsupported | only image |
| VA | [Yuengling Shamrock Marathon Weekend](https://www.shamrockmarathon.com/marathon/) | Marathon | unsupported | only image |
| VA | [Bayport Credit Union Surf N Santa 5 Miler](https://www.surfnsanta5miler.com/5-miler/) | 5 Miler | unsupported | only image, pdf |
| VA | [Chartway Virginia Beach 10 Miler & 5K](https://virginiabeach10miler.com/10-miler/) | 10 Miler | unsupported | only image, pdf |
| VA | [Chartway Virginia Beach 10 Miler & 5K](https://virginiabeach10miler.com/5k/) | 5K | unsupported | only image, pdf |
| VA | [Wicked 10K Weekend](https://wicked10k.com/10k/) | 10K | unsupported | only image, pdf |
| VA | [Wicked 10K Weekend](https://wicked10k.com/5k/) | 5K | unsupported | only image, pdf |
| VT | [Half Marathon Unplugged](https://www.runvermont.org/half-marathon-unplugged/course-map/) | Half Marathon | unsupported | only image |
| VT | [M&T Bank Vermont City Marathon](https://www.runvermont.org/vermont-city-marathon-relay/course-map/) | Marathon | unsupported | only image, pdf |
| WA | [UW Medicine Seattle Marathon](https://www.seattlemarathon.org/) | Half Marathon | no-source | no course map on https://www.seattlemarathon.org/ |
| WA | [UW Medicine Seattle Marathon](https://www.seattlemarathon.org/) | Marathon | no-source | no course map on https://www.seattlemarathon.org/ |
| WA | [St. Patrick's Day Dash](https://stpatsdash.com/race-info/) | 5K | unsupported | only pdf |
| WI | [Bellin Run](https://www.bellinrun.com/event-information) | 10K | no-source | no course map on https://www.bellinrun.com/, https://www.bellinrun.com/event-information, https://www.bellinrun.com/results-records/course-records |
| WI | [Bellin Run](https://www.bellinrun.com/event-information) | 5K | no-source | no course map on https://www.bellinrun.com/, https://www.bellinrun.com/event-information, https://www.bellinrun.com/results-records/course-records |
| WI | [Madison Marathon](https://www.madisonmarathon.org/) | Marathon | no-source | no course map on https://www.madisonmarathon.org/ |
| WI | [Milwaukee Lakefront Marathon](https://www.milwaukeelakefrontmarathon.org/marathon-map) | Marathon | no-source | no course map on https://www.milwaukeelakefrontmarathon.org/, https://www.milwaukeelakefrontmarathon.org/marathon-map |
