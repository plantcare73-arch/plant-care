import os
import certifi
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

def get_disease_dataset():
    now = datetime.now(timezone.utc)
    
    # 38 Classes metadata
    classes_meta = [
        # Apple
        ("Apple___Apple_scab", "Apple", "Apple Scab", 
         "Fungal infection caused by Venturia inaequalis leading to olive-green or dark velvety lesions on leaves and fruit scabs.",
         ["Olive-green to dark brown velvety spots on upper leaf surfaces.", "Yellowing and premature leaf fall.", "Scabby, corky lesions on fruit."],
         ["Rake and compost or destroy fallen leaves in autumn.", "Plant disease-resistant varieties such as Honeycrisp or Liberty.", "Ensure adequate canopy pruning for rapid leaf drying."],
         ["Spray organic neem oil extract or copper soap early in the season.", "Apply sulfur spray at bud break."],
         ["Apply fungicides containing myclobutanil, captan, or mancozeb at tight cluster stages."]),
        
        ("Apple___Black_rot", "Apple", "Black Rot",
         "Fungal disease caused by Botryosphaeria obtusa affecting leaves (frogeye leaf spot), fruit, and limbs.",
         ["Small purple specks on leaves that enlarge to round brown spots with purple margins (frogeye pattern).", "Black rotting lesions on fruit.", "Bark cankers on branches."],
         ["Prune out dead wood, twigs, and mummified fruit from previous season.", "Disinfect pruning shears between cuts."],
         ["Apply bio-fungicides containing Bacillus subtilis or liquid copper formulations."],
         ["Apply thiophanate-methyl or captan sprays from pink bud through petal fall."]),
        
        ("Apple___Cedar_apple_rust", "Apple", "Cedar Apple Rust",
         "Fungal disease caused by Gymnosporangium juniperi-virginianae requiring both juniper and apple trees to complete its life cycle.",
         ["Bright yellow-orange spots on leaves that swell.", "Small tube-like projections forming on the underside of leaves.", "Distorted yellow lesions on young fruits."],
         ["Remove eastern red cedar and juniper trees within 1-2 miles if possible.", "Plant resistant cultivars like Redfree, Prima, or Enterprise."],
         ["Apply sulfur or copper octanoate sprays at pink bud and petal drop."],
         ["Apply myclobutanil or mancozeb when orange gelatinous galls appear on nearby cedars."]),
         
        ("Apple___healthy", "Apple", "Healthy Apple Leaf",
         "The leaf tissue is vibrant, vigorous, and free from pathogenic spots, mildew, or nutrient deficiencies.",
         ["Vibrant green foliage with smooth margins and no visible spotting."],
         ["Continue balanced irrigation and nitrogen-potassium fertilization.", "Maintain regular pest monitoring."],
         ["Use compost tea for foliar immunity boost."], []),

        # Blueberry
        ("Blueberry___healthy", "Blueberry", "Healthy Blueberry",
         "Healthy blueberry foliage showing characteristic waxy sheen, absence of mummification or rust.",
         ["Clean dark green leaves with no necrotic borders or chlorosis."],
         ["Maintain soil pH between 4.5 and 5.2 using elemental sulfur.", "Keep roots moist with pine bark mulch."],
         [], []),

        # Cherry
        ("Cherry_(including_sour)___Powdery_mildew", "Cherry (including sour)", "Powdery Mildew",
         "Fungal disease caused by Podosphaera clandestina resulting in white fungal growth on young leaves and fruit deformity.",
         ["White powdery fungal patches on new leaf growth.", "Leaves curl upward, distort, and become brittle.", "Stunted shoot elongation."],
         ["Prune dense canopy to improve sunlight penetration and air movement.", "Avoid overhead irrigation that elevates humidity."],
         ["Apply potassium bicarbonate, neem oil, or horticultural oils on early onset.", "Milk-water foliar sprays (1:9 ratio) can reduce spore germination."],
         ["Apply sulfur-based fungicides or myclobutanil at petal fall and shuck split.", "Wear protective goggles and respirator during chemical dusting."]),

        ("Cherry_(including_sour)___healthy", "Cherry (including sour)", "Healthy Cherry Leaf",
         "Lush, glossy green cherry leaves exhibiting robust photosynthesis and normal vascular structure.",
         ["Glossy deep green leaf surface without shot-holes or powdery residues."],
         ["Ensure adequate root zone drainage.", "Monitor for early aphid or borer activity."],
         [], []),

        # Corn
        ("Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn (Maize)", "Cercospora / Gray Leaf Spot",
         "Fungal disease caused by Cercospora zeae-maydis. Causes rectangular tan to gray spots running parallel to leaf veins.",
         ["Small rectangular necrotic lesions restricted by veins.", "Lesions merge into extensive leaf blights during humid weather."],
         ["Rotate crops with non-grasses (soybean, legumes) for at least 1-2 years.", "Till under crop residues to accelerate breakdown."],
         ["Apply Trichoderma viride or Pseudomonas fluorescens as bio-control foliar agents."],
         ["Apply strobilurin or triazole fungicides (e.g. azoxystrobin) at tassel emergence if disease index is high."]),

        ("Corn_(maize)___Common_rust_", "Corn (Maize)", "Common Rust",
         "Fungal infection caused by Puccinia sorghi characterized by cinnamon-brown pustules on both leaf surfaces.",
         ["Small golden-brown to dark cinnamon pustules on both upper and lower leaf surfaces.", "Pustules erupt releasing powdery reddish-brown spores."],
         ["Plant certified rust-resistant maize hybrids.", "Plant early in the season to evade peak spore showers."],
         ["Dust with bio-fungicide sulfur sprays if detected at early vegetative stages."],
         ["Apply pyraclostrobin or tebuconazole if rust reaches the ear leaf before blister stage."]),

        ("Corn_(maize)___Northern_Leaf_Blight", "Corn (Maize)", "Northern Leaf Blight",
         "Fungal disease caused by Exserohilum turcicum causing large cigar-shaped grayish-green to tan lesions.",
         ["Elongated, elliptical 'cigar-shaped' lesions 1 to 6 inches long.", "Olive-gray velvety spore layer in lesion centers during wet mornings."],
         ["Choose resistant hybrid seed with Ht genes.", "Bury infected debris after harvest."],
         ["Bio-fungicides like Bacillus amyloliquefaciens can suppress early spore germination."],
         ["Apply propiconazole or azoxystrobin at early tasseling stage."]),

        ("Corn_(maize)___healthy", "Corn (Maize)", "Healthy Corn",
         "Vigorous corn leaf with strong parallel venation, crisp green hue, and no fungal pustules or blight stripes.",
         ["Broad, deep green leaves with crisp edges and clean leaf collars."],
         ["Provide split-nitrogen applications at V4 and V8 stages.", "Maintain consistent moisture during silking."],
         [], []),

        # Grape
        ("Grape___Black_rot", "Grape", "Black Rot",
         "Caused by Guignardia bidwellii. Highly destructive to fruit clusters, turning grapes into hard shriveled black mummies.",
         ["Circular tan leaf spots with tiny black dots (pycnidia) arranged in rings.", "Grapes turn brown, soften, and quickly shrivel into black mummies."],
         ["Remove and burn mummified grape clusters during winter pruning.", "Keep grape canopy open with shoot positioning."],
         ["Apply liquid copper or wettable sulfur formulations at early bloom."],
         ["Spray mancozeb, myclobutanil, or captan from bud break until veraison."]),

        ("Grape___Esca_(Black_Measles)", "Grape", "Esca (Black Measles)",
         "Complex fungal vascular disease causing 'tiger-stripe' interveinal chlorosis and necrotic spots on berries.",
         ["Interveinal yellowing and browning creating a striking tiger-stripe pattern.", "Dark purple or black spotting ('measles') on ripening berries."],
         ["Avoid large pruning cuts in rainy weather; seal wounds with pruning sealant.", "Remove severely infected vines from the vineyard."],
         ["Trunk renewal through sucker training."],
         ["Remedial surgery by excising decayed wood and treating cuts with benomyl paste."]),

        ("Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape", "Leaf Blight (Isariopsis)",
         "Fungal disease caused by Pseudocercospora cladosporioides causing irregular dark brown patches.",
         ["Irregularly shaped dark brown spots with darker margins.", "Premature defoliation starting from basal leaves."],
         ["Prune excess foliage to allow maximum sunlight into the fruiting zone."],
         ["Apply Bordeaux mixture (1%) or copper oxychloride."],
         ["Spray carbendazim or difenoconazole at early disease manifestation."]),

        ("Grape___healthy", "Grape", "Healthy Grape Vine",
         "Vibrant grape foliage with strong palmate lobing, free from powdery deposits, black rot spots, or wilting.",
         ["Healthy palmate leaves with vivid green coloring and healthy tendrils."],
         ["Regular canopy management and balanced potassium feeding."],
         [], []),

        # Orange
        ("Orange___Haunglongbing_(Citrus_greening)", "Orange (Citrus)", "Huanglongbing (Citrus Greening)",
         "Bacterial disease caused by Candidatus Liberibacter asiaticus, transmitted by the Asian citrus psyllid.",
         ["Asymmetrical blotchy mottle on leaves across veins.", "Yellow shoots on individual branches.", "Small, lopsided fruit that stays green at the bottom and tastes bitter."],
         ["Scout and control the Asian citrus psyllid vector aggressively.", "Plant certified disease-free nursery stock under insect-proof screenhouses.", "Eradicate confirmed infected trees to stop regional spread."],
         ["Apply horticultural mineral oil or neem oil to suppress psyllid nymphs."],
         ["Apply targeted insecticides (imidacloprid, thiamethoxam) to manage vector populations."]),

        # Peach
        ("Peach___Bacterial_spot", "Peach", "Bacterial Spot",
         "Caused by Xanthomonas arboricola pv. pruni. Causes angular water-soaked leaf spots and deep pitting on fruit.",
         ["Small, angular, water-soaked spots that turn purple-brown and drop out, leaving 'shot-holes'.", "Deep cracked gumming pits on fruit."],
         ["Plant tolerant peach varieties (e.g. Harrow Diamond, Candor).", "Provide windbreaks to minimize blowing sand leaf abrasions."],
         ["Apply copper hydroxide during dormant and bud-swell stages."],
         ["Apply oxytetracycline sprays during bloom and petal fall."]),

        ("Peach___healthy", "Peach", "Healthy Peach",
         "Smooth lanceolate peach leaves displaying rich green hue and healthy petiolar glands.",
         ["Glossy, vibrant lance-shaped leaves with unblemished surfaces."],
         ["Maintain regular dormant winter sprays and soil organic matter."],
         [], []),

        # Pepper, bell
        ("Pepper,_bell___Bacterial_spot", "Bell Pepper", "Bacterial Spot",
         "Caused by Xanthomonas campestris pv. vesicatoria. Leads to severe defoliation and sunken fruit lesions.",
         ["Small, circular, water-soaked dark spots on leaves.", "Lesions become necrotic with yellow halos.", "Leaves turn yellow and drop rapidly."],
         ["Use hot-water treated or certified disease-free seeds.", "Avoid overhead sprinkler irrigation; use drip lines."],
         ["Foliar sprays of copper soap combined with bio-stimulants."],
         ["Spray copper fungicides mixed with mancozeb for enhanced bactericidal action."]),

        ("Pepper,_bell___healthy", "Bell Pepper", "Healthy Bell Pepper",
         "Crisp, deep green leaves without blistering, mosaic mottling, or edge necrosis.",
         ["Uniform dark green foliage, sturdy stem nodes, and healthy flower blossoms."],
         ["Keep soil evenly moist to avoid blossom end rot and calcium deficiency."],
         [], []),

        # Potato
        ("Potato___Early_blight", "Potato", "Early Blight",
         "Caused by Alternaria solani. Notable for concentric target-board brown rings on older leaves.",
         ["Dark brown to black spots with concentric rings ('target board').", "Yellow halo around mature spots.", "Lower leaves dry up and droop along the stem."],
         ["Practice 3-year crop rotation avoiding solanaceous crops.", "Ensure adequate spacing for good airflow."],
         ["Apply bio-fungicides based on Trichoderma harzianum or Bacillus subtilis."],
         ["Apply chlorothalonil, mancozeb, or azoxystrobin at early symptom onset."]),

        ("Potato___Late_blight", "Potato", "Late Blight",
         "Devastating oomycete Phytophthora infestans causing water-soaked dark lesions and white underleaf sporulation.",
         ["Water-soaked pale spots turning purplish-black.", "Fluffy white mold growth on the undersides of leaves in humid mornings.", "Foul odor in fields as foliage collapses."],
         ["Destroy volunteer potato plants and cull piles.", "Plant certified disease-free seed tubers."],
         ["Apply copper oxychloride preventively before rain spells."],
         ["Apply metalaxyl, cymoxanil, or dimethomorph immediately upon local disease alerts."]),

        ("Potato___healthy", "Potato", "Healthy Potato",
         "Lush green potato canopy with vigorous compound leaves and active tuber development.",
         ["Clean compound leaves without water soaking or target lesions."],
         ["Hilling up soil around base to protect developing tubers."],
         [], []),

        # Raspberry
        ("Raspberry___healthy", "Raspberry", "Healthy Raspberry",
         "Healthy raspberry foliage showing serrated trifoliate leaves with clean silvery undersides.",
         ["Bright green cane leaves free of anthracnose spots or yellow rust."],
         ["Prune out spent floricanes after fruiting."],
         [], []),

        # Soybean
        ("Soybean___healthy", "Soybean", "Healthy Soybean",
         "Strong trifoliate soybean leaves with uniform nitrogen fixation and no Asian rust pustules.",
         ["Crisp green trifoliate foliage free of frogeye spots."],
         ["Inoculate seeds with Bradyrhizobium for natural nitrogen fertility."],
         [], []),

        # Squash
        ("Squash___Powdery_mildew", "Squash / Cucurbit", "Powdery Mildew",
         "Fungal infection caused by Podosphaera xanthii covering broad squash leaves in talcum-like white film.",
         ["White powdery spots appearing on older leaves and stems.", "Patches coalesce to coat the entire leaf surface.", "Leaves turn brown, wither, and die prematurely."],
         ["Choose resistant squash cultivars.", "Plant in full sun and space vines adequately."],
         ["Apply potassium bicarbonate, diluted milk spray (10-20%), or neem oil at first white specks."],
         ["Apply myclobutanil or tebuconazole according to label directions."]),

        # Strawberry
        ("Strawberry___Leaf_scorch", "Strawberry", "Leaf Scorch",
         "Fungal disease caused by Diplocarpon earlianum causing purple spots that coalesce into scorched patches.",
         ["Numerous small, irregular purple or dark brown blotches.", "Leaves appear burned or scorched as blotches merge.", "Fruit production drops dramatically."],
         ["Remove infected dead foliage after spring harvest.", "Avoid prolonged leaf wetness through drip irrigation."],
         ["Apply copper-based organic fungicides before bloom."],
         ["Apply captan or dodine during early leaf emergence."]),

        ("Strawberry___healthy", "Strawberry", "Healthy Strawberry",
         "Vibrant trifoliate strawberry foliage, healthy runners, and bright green crowns.",
         ["Glossy, vibrant green trifoliate leaves with serrated edges."],
         ["Maintain clean straw mulch to keep leaves off damp soil."],
         [], []),

        # Tomato
        ("Tomato___Bacterial_spot", "Tomato", "Bacterial Spot",
         "Caused by Xanthomonas species. Causes small greasy water-soaked specks with yellow halos on foliage and scabby spots on fruit.",
         ["Small, dark, water-soaked spots (1-3mm) with yellow halos.", "Spots may tear or fall out, giving a ragged look.", "Rough scabby spots on fruit surface."],
         ["Avoid handling plants when wet.", "Drip irrigate at root base rather than overhead spraying."],
         ["Spray copper soap formulations weekly during humid spells."],
         ["Apply copper hydroxide mixed with mancozeb at first sign."]),

        ("Tomato___Early_blight", "Tomato", "Early Blight",
         "Caused by Alternaria linariae. Targets lower older leaves with dark concentric ring lesions.",
         ["Concentric target-board brown rings on bottom leaves.", "Leaves yellow and drop, exposing green tomatoes to sunscald."],
         ["Prune bottom 12 inches of foliage to prevent soil splash.", "Mulch base of plants heavily with straw or landscape fabric."],
         ["Foliar sprays of copper fungicide or Serenade (Bacillus subtilis)."],
         ["Apply chlorothalonil or azoxystrobin every 7-10 days."]),

        ("Tomato___Late_blight", "Tomato", "Late Blight",
         "Caused by Phytophthora infestans. Rapidly blights foliage and leaves greasy brown firm rot on fruit.",
         ["Large, dark, water-soaked lesions that spread rapidly.", "White fuzzy mold on leaf undersides in morning humidity.", "Greasy brown sunken patches on green or ripe tomatoes."],
         ["Plant resistant varieties like Mountain Magic or Defiant.", "Immediately remove and seal blighted plants in trash bags."],
         ["Preventive sprays of copper octanoate before wet weather."],
         ["Apply cymoxanil, mandipropamid, or chlorothalonil upon alert."]),

        ("Tomato___Leaf_Mold", "Tomato", "Leaf Mold",
         "Caused by Passalora fulva. Thrives in high greenhouse humidity, producing pale yellow patches above and olive-velvet mold below.",
         ["Pale greenish-yellow spots on upper leaf surfaces.", "Olive-green to brown velvety fungal growth directly underneath the spots.", "Leaves wilt and drop."],
         ["Improve greenhouse or tunnel ventilation with exhaust fans.", "Maintain relative humidity below 85%."],
         ["Apply bio-fungicides or neem oil."],
         ["Apply copper fungicides or chlorothalonil."]),

        ("Tomato___Septoria_leaf_spot", "Tomato", "Septoria Leaf Spot",
         "Caused by Septoria lycopersici. Tiny circular spots with pale gray centers and dark borders pepper lower leaves.",
         ["Numerous tiny (2-3mm) circular spots with grayish-white centers and dark brown margins.", "Tiny black specks (pycnidia) inside lesion centers."],
         ["Never work in tomato patch when foliage is wet.", "Remove infected lower leaves promptly.", "Rotate away from tomatoes/peppers for 2 years."],
         ["Copper sulfate sprays applied at first leaf spots."],
         ["Apply mancozeb or chlorothalonil regularly."]),

        ("Tomato___Spider_mites Two-spotted_spider_mite", "Tomato", "Two-Spotted Spider Mites",
         "Microscopic pests (Tetranychus urticae) that puncture leaf cells, creating fine white/yellow stippling and webbing.",
         ["Fine yellow stippling or bronzing on leaf surface.", "Silken webbing underneath leaves and at stem junctions.", "Leaves dry out, turn brittle, and fall off."],
         ["Hose down foliage with strong jet of water to knock down populations.", "Avoid broad-spectrum synthetic pesticides that kill predatory mites."],
         ["Release predatory mites (Phytoseiulus persimilis).", "Spray insecticidal soap, rosemary oil, or neem oil."],
         ["Apply abamectin or bifenazate miticide if infestation is severe."]),

        ("Tomato___Target_Spot", "Tomato", "Target Spot",
         "Caused by Corynespora cassiicola. Brown circular lesions with distinctive concentric rings on leaves and fruit.",
         ["Brown circular lesions with concentric rings and chlorotic halos.", "Lesions may crack in centers."],
         ["Avoid overhead watering; prune canopy to increase sunlight penetration."],
         ["Apply bio-fungicides or copper hydroxide."],
         ["Spray pyraclostrobin or chlorothalonil."]),

        ("Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato", "Tomato Yellow Leaf Curl Virus (TYLCV)",
         "Viral pathogen transmitted by sweetpotato whitefly (Bemisia tabaci). Causes severe stunting and upward curling of leaves.",
         ["Severe upward cupping and curling of leaf margins.", "Marked yellowing (chlorosis) along leaf margins.", "Severe stunting of plant growth and aborted flowers."],
         ["Use yellow sticky traps to detect whiteflies early.", "Use 50-mesh insect-proof netting in seedling nurseries.", "Pull out and destroy virus-infected plants immediately."],
         ["Spray neem oil or horticultural soap to suppress whitefly nymphs."],
         ["Apply systemic insecticides like imidacloprid to control vector whiteflies."]),

        ("Tomato___Tomato_mosaic_virus", "Tomato", "Tomato Mosaic Virus (ToMV)",
         "Mechanically transmitted Tobamovirus causing mottled light and dark green mosaic patterns on foliage.",
         ["Mottled light and dark green mosaic pattern on leaves.", "Distorted, blistered, or shoestring-like narrow leaves.", "Uneven fruit ripening with internal brown rings."],
         ["Wash hands with soap and dip tools in 20% non-fat milk solution before handling plants.", "Never smoke or handle tobacco near tomato plants."],
         ["Remove and destroy infected plants; do not compost."],
         ["No chemical cure exists for viral plant infections. Focus on hygiene and resistant seed."]),

        ("Tomato___healthy", "Tomato", "Healthy Tomato",
         "Vigorous tomato plant exhibiting strong green compound leaves, sturdy stems, and active flower clusters.",
         ["Lush green foliage free of fungal spotting, curling, or mite webs."],
         ["Prune suckers for better air circulation and support vines with strong stakes or cages."],
         ["Foliar compost tea or seaweed extract for enhanced natural resistance."],
         [])
    ]
    
    diseases = []
    treatments = []
    
    for item in classes_meta:
        class_name, crop, disease_name, desc, symptoms, prev_steps, org_steps, chem_steps = item
        
        diseases.append({
            'class_name': class_name,
            'crop': crop,
            'disease_name': disease_name,
            'description': desc,
            'symptoms': symptoms,
            'created_at': now
        })
        
        if prev_steps:
            treatments.append({
                'disease_class': class_name,
                'category': 'preventive',
                'instructions': prev_steps,
                'safety_warnings': []
            })
        if org_steps:
            treatments.append({
                'disease_class': class_name,
                'category': 'organic',
                'instructions': org_steps,
                'safety_warnings': ['Always patch-test organic foliar oils on 2-3 leaves 24 hours prior to full canopy spraying.']
            })
        if chem_steps:
            treatments.append({
                'disease_class': class_name,
                'category': 'chemical',
                'instructions': chem_steps,
                'safety_warnings': [
                    'Wear protective nitrile gloves, protective eyewear, and face mask during chemical spraying.',
                    'Strictly adhere to the pre-harvest interval (PHI) before consuming or selling harvested produce.',
                    'Never spray during windy conditions or near open water bodies.'
                ]
            })
            
    return diseases, treatments


def seed():
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DATABASE_NAME", "plant_disease_db")
    print(f"Connecting to MongoDB: {mongo_uri[:35]}... (DB: {db_name})")
    
    kwargs = {}
    if "mongodb+srv" in mongo_uri or "ssl=true" in mongo_uri.lower():
        kwargs["tlsCAFile"] = certifi.where()

    client = MongoClient(mongo_uri, **kwargs)
    db = client[db_name]
    
    print("Clearing old diseases/treatments...")
    db['diseases'].delete_many({})
    db['treatments'].delete_many({})
    
    diseases, treatments = get_disease_dataset()
    
    print(f"Inserting {len(diseases)} diseases into 'diseases' collection...")
    db['diseases'].insert_many(diseases)
    
    print(f"Inserting {len(treatments)} treatment plans into 'treatments' collection...")
    db['treatments'].insert_many(treatments)
    
    print("Seeding complete! All 38 classes and treatments seeded successfully.")

if __name__ == "__main__":
    seed()
