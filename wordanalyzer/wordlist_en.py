#!/usr/bin/env python3

WORD_COLLECTION_EN = set(sorted([
	  u'culprit'
	, u'cunning'
	, u'curious'
	, u'deduction'
	, u'deliberate'
	, u'deprived'
	, u'detention'
	, u'devoid'
	, u'disdainful'
	, u'disgruntled'
	, u'distinct'
	, u'diversion'
	, u'don\'t everybody speak up at once!'
	, u'drawer'
	, u'dreadful'
	, u'dregs'
	, u'drenched'
	, u'dusk'
	, u'eerie'
	, u'elaborate'
	, u'emaciated'
	, u'to pledge'
	, u'to ponder (on sth.)'
	, u'to prepone sth.'
	, u'to profess'
	, u'to propose'
	, u'to pursue'
	, u'to reciprocate'
	, u'to recite'
	, u'to reckon'
	, u'to recline'
	, u'to recoil'
	, u'to redeem'
	, u'to reek'
	, u'to refute'
	, u'to regress'
	, u'to rejuvenate'
	, u'to resent'
	, u'to size sb. up'
	, u'to slander'
	, u'to stifle'
	, u'to subdue'
	, u'to succumb'
	, u'to sully'
	, u'to swipe'
	, u'to treasure'
	, u'to uphold'
	, u'to vet'
	, u'to walk on eggshells'
	, u'travesty'
	, u'treacherous'
	, u'trembling'
	, u'tremor'
	, u'tribulation'
	, u'trident'
	, u'ubiquitous'
	, u'ulcer'
	, u'ulterior'
	, u'umbilical cord'
	, u'unanimously'
	, u'undue'
	, u'unencumbered'
	, u'unfathomable'
	, u'unfettered'
	, u'unrelenting'
	, u'up the creek'
	, u'upheaval'
	, u'uxoricide'
	, u'vacuous'
	, u'vain'
	, u'valorous'
	, u'vast'
	, u'verbatim'
	, u'vernacular'
	, u'vibrant'
	, u'vicarious'
	, u'vicinity'
	, u'vigilante'
	, u'voluble'
	, u'votive'
	, u'vying'
	, u'wacky'
	, u'wager'
	, u'warranty'
	, u'whim'
	, u'wits'
	, u'zaftig'
	, u'abashed'
	, u'aggravating'
	, u'aggrieved'
	, u'aghast'
	, u'agitated'
	, u'antagonizing'
	, u'appalled'
	, u'aquiver'
	, u'austere'
	, u'awestruck'
	, u'bated'
	, u'battered'
	, u'beckoning'
	, u'bedlam'
	, u'bedraggled'
	, u'blistering'
	, u'blundering'
	, u'boisterous'
	, u'breezy'
	, u'burrowed'
	, u'chipped'
	, u'commiserating'
	, u'comprehensive'
	, u'compulsory'
	, u'contemptuous'
	, u'convulsive'
	, u'crestfallen'
	, u'crowing'
	, u'askance'
	, u'askew'
	, u'amber'
	, u'clairvoyant'
	, u'copper'
	, u'airily'
	, u'amicably'
	, u'apprehensively'
	, u'astray'
	, u'astride'
	, u'at large'
	, u'benignly'
	, u'blandly'
	, u'briskly'
	, u'crisply'
	, u'a pregnant pause'
	, u'acquaintance'
	, u'animosity'
	, u'antics'
	, u'apprentice'
	, u'archway'
	, u'asperity'
	, u'assent'
	, u'axle grease'
	, u'balaclava'
	, u'banshee'
	, u'barter'
	, u'bauble'
	, u'beacon'
	, u'berth'
	, u'bigotry'
	, u'bird of prey'
	, u'blazing row'
	, u'blemish'
	, u'blunder'
	, u'bog'
	, u'bogey'
	, u'bonnet'
	, u'boughs'
	, u'boulder'
	, u'brass'
	, u'brim'
	, u'bungler'
	, u'burrow'
	, u'cane'
	, u'canopy'
	, u'cauldron'
	, u'charm'
	, u'chisel'
	, u'chivalry'
	, u'cinch'
	, u'cloak'
	, u'coil'
	, u'commodity'
	, u'commotion'
	, u'concealment'
	, u'condemnation'
	, u'conduct'
	, u'cowardice'
	, u'crate'
	, u'crescendo'
	, u'crest'
	, u'amid'
	, u'to appraise'
	, u'at either end'
	, u'agonising'
	, u'counselling'
	, u'barmy'
	, u'chuffed'
	, u'bloke'
	, u'chappie'
	, u'codger'
	, u'curtly'
	, u'custard'
	, u'dejectedly'
	, u'derisive'
	, u'diatribe'
	, u'diminished'
	, u'distended'
	, u'dodgy'
	, u'dolefully'
	, u'dormice'
	, u'dottiness'
	, u'downtrodden'
	, u'draught'
	, u'draughty'
	, u'drawling'
	, u'duffer'
	, u'emblazoned'
	, u'emerald'
	, u'enclosure'
	, u'engorgement'
	, u'engulfed'
	, u'enraptured'
	, u'enticing'
	, u'entwined'
	, u'exasperated'
	, u'exuberant'
	, u'fainted'
	, u'fervent'
	, u'feverishly'
	, u'flabbergasted'
	, u'fleet'
	, u'flight of stairs'
	, u'fluke'
	, u'flustered'
	, u'fondly'
	, u'fortnight'
	, u'frame-up'
	, u'frantic'
	, u'fringe'
	, u'fudge'
	, u'fugitive'
	, u'furling'
	, u'furtive'
	, u'gales of laughter'
	, u'gallant'
	, u'galvanised'
	, u'gamekeeper'
	, u'gash'
	, u'gaunt'
	, u'gawping'
	, u'gaze'
	, u'gibbon'
	, u'gills'
	, u'gingerly'
	, u'glee'
	, u'gloomily'
	, u'glowering'
	, u'goblets'
	, u'gouge'
	, u'gravely'
	, u'gravy'
	, u'griffin'
	, u'grisly'
	, u'grubby'
	, u'gruffly'
	, u'guffaw'
	, u'guile'
	, u'hag'
	, u'hampered'
	, u'harebrained'
	, u'harness'
	, u'havoc'
	, u'hearthrug'
	, u'hedgehog'
	, u'heinous'
	, u'henceforth'
	, u'hewn'
	, u'hilt'
	, u'hinge'
	, u'hitch'
	, u'hitherto'
	, u'hoarse'
	, u'holly'
	, u'hoodwinked'
	, u'huddle'
	, u'humongous'
	, u'hunchback'
	, u'hunched'
	, u'impeccably'
	, u'imperiously'
	, u'imploringly'
	, u'incantation'
	, u'incidentally'
	, u'indignantly'
	, u'indispensable'
	, u'indisposed'
	, u'inept'
	, u'inquiry'
	, u'inscrutable'
	, u'insurmountable'
	, u'interrogating'
	, u'intrigued'
	, u'irksome'
	, u'jauntily'
	, u'jaunty'
	, u'javelin'
	, u'jig'
	, u'jowl'
	, u'kettle'
	, u'knack'
	, u'laden'
	, u'landing'
	, u'lap of honor'
	, u'lavatory seat'
	, u'layabout'
	, u'legible'
	, u'lenient'
	, u'lest'
	, u'liability'
	, u'lofty'
	, u'longingly'
	, u'lopsided'
	, u'lot'
	, u'ludicrous'
	, u'lumbago'
	, u'lump'
	, u'maddening'
	, u'makeshift'
	, u'malice'
	, u'manacle'
	, u'mantelpiece'
	, u'manure'
	, u'marble'
	, u'marsh'
	, u'mead'
	, u'meadow'
	, u'meddlesome'
	, u'menace'
	, u'menacing'
	, u'mingled'
	, u'mirthless'
	, u'misty'
	, u'mongrel'
	, u'moodily'
	, u'moral fibre'
	, u'mortal peril'
	, u'mulishly'
	, u'mundane'
	, u'mutinous'
	, u'nonplussed'
	, u'nostrils'
	, u'nosy'
	, u'oaf'
	, u'objection'
	, u'offhand'
	, u'old-fangled'
	, u'omission'
	, u'ordeal'
	, u'outskirts'
	, u'overt'
	, u'pace'
	, u'paddock'
	, u'pallid'
	, u'paramount'
	, u'parchment'
	, u'parlour'
	, u'patch'
	, u'paving'
	, u'pebbles'
	, u'peckish'
	, u'pelting'
	, u'penance'
	, u'pensively'
	, u'perch'
	, u'perchance'
	, u'perturbed'
	, u'petrified'
	, u'petulantly'
	, u'pewter'
	, u'pheasant'
	, u'phial'
	, u'pillock'
	, u'pincers'
	, u'pinprick'
	, u'pinstriped'
	, u'plinth'
	, u'plumbing'
	, u'plus fours'
	, u'poker'
	, u'polecat'
	, u'porridge'
	, u'portly'
	, u'potholes'
	, u'precarious'
	, u'premeditated'
	, u'premise'
	, u'premonition'
	, u'preposterous'
	, u'preserve'
	, u'profusely'
	, u'prong'
	, u'protruding'
	, u'protuberant'
	, u'provision'
	, u'prowling'
	, u'prudent'
	, u'pug'
	, u'pummeling'
	, u'punitive'
	, u'putrid'
	, u'puzzlement'
	, u'quagmire'
	, u'queasy'
	, u'quick-witted'
	, u'quill'
	, u'raccoon'
	, u'rag doll'
	, u'rancid'
	, u'rapturously'
	, u'raspberry'
	, u'rattled'
	, u'raucous'
	, u'ravine'
	, u'receding'
	, u'rein'
	, u'relish'
	, u'remedy'
	, u'reminiscent'
	, u'remnant'
	, u'remorse'
	, u'reproachful'
	, u'reprovingly'
	, u'resemblance'
	, u'resentment'
	, u'retaliation'
	, u'retention'
	, u'reverie'
	, u'revulsion'
	, u'rickety'
	, u'riddle'
	, u'rigid'
	, u'rooster'
	, u'ruffled'
	, u'rug'
	, u'rummaging'
	, u'sanctimoniously'
	, u'saucer'
	, u'savagely'
	, u'savouring'
	, u'sb. humbugs'
	, u'sb. purports'
	, u'scabbard'
	, u'scarlet'
	, u'scathing'
	, u'scowling'
	, u'scrounger'
	, u'scudding'
	, u'scuffle'
	, u'seal'
	, u'search me.'
	, u'secluded'
	, u'seething'
	, u'shallow'
	, u'shamrock'
	, u'shan\'t'
	, u'sheaf'
	, u'shifty'
	, u'shrub'
	, u'silkily'
	, u'sinew'
	, u'slab'
	, u'slain'
	, u'slithering'
	, u'sliver'
	, u'slog'
	, u'sluggish'
	, u'sly'
	, u'smirk'
	, u'snuff box'
	, u'solemnly'
	, u'sombre'
	, u'somersault'
	, u'soot'
	, u'sore'
	, u'spasm'
	, u'spectacles'
	, u'spinning top'
	, u'spotty'
	, u'sprouts'
	, u'spunky'
	, u'squashy'
	, u'squeal'
	, u'squid'
	, u'squirt'
	, u'stag'
	, u'stagecoach'
	, u'staggered'
	, u'startled'
	, u'steering'
	, u'stern'
	, u'stifling'
	, u'stoat'
	, u'strain'
	, u'subdued'
	, u'sullenness'
	, u'supple'
	, u'surly'
	, u'swarthy'
	, u'swathed'
	, u'swiftly'
	, u'talon'
	, u'tankard'
	, u'tantrum'
	, u'tap'
	, u'tawny'
	, u'teeming'
	, u'tentatively'
	, u'tenterhook'
	, u'tersely'
	, u'testily'
	, u'tetchy'
	, u'tethered'
	, u'thatched'
	, u'threshold'
	, u'thud'
	, u'tichy'
	, u'timidly'
	, u'to attain'
	, u'to bait'
	, u'to bask'
	, u'to be all of a dither'
	, u'to be delicate'
	, u'to be immersed'
	, u'to be just doing sth.'
	, u'to be keen on sth.'
	, u'to be over the moon with sth.'
	, u'to be startled'
	, u'to be up to scratch'
	, u'to be wary of sb./sth.'
	, u'to be well shot of sb.'
	, u'to beam'
	, u'to beckon'
	, u'to bellow'
	, u'to bequeath'
	, u'to bestow'
	, u'to betide'
	, u'to blanch'
	, u'to blow sb. a raspberry'
	, u'to blush'
	, u'to boom'
	, u'to brandish'
	, u'to budge up'
	, u'to cackle'
	, u'to canter'
	, u'to catcall'
	, u'to catch sb. red-handed'
	, u'to cheek sb.'
	, u'to chortle'
	, u'to clasp'
	, u'to clout'
	, u'to clutch'
	, u'to collude'
	, u'to commend'
	, u'to commute'
	, u'to conceal'
	, u'to confine'
	, u'to congregate'
	, u'to conjure'
	, u'to consent'
	, u'to convey'
	, u'to crease'
	, u'to culminate'
	, u'to daze'
	, u'to deceive'
	, u'to defer'
	, u'to demise'
	, u'to dent'
	, u'to deprive'
	, u'to desist'
	, u'to despise'
	, u'to detain'
	, u'to detest'
	, u'to diminish'
	, u'to discern'
	, u'to disembowel'
	, u'to dispatch'
	, u'to dispense'
	, u'to divulge'
	, u'to double back'
	, u'to double up'
	, u'to dread'
	, u'to each his own'
	, u'to eavesdrop'
	, u'to egg sb. on'
	, u'to elude'
	, u'to emblazon'
	, u'to emerge'
	, u'to ensnare'
	, u'to exclaim'
	, u'to expel'
	, u'to faint'
	, u'to falter'
	, u'to fancy'
	, u'to fathom'
	, u'to feint'
	, u'to fidget'
	, u'to flay'
	, u'to flinch'
	, u'to forage'
	, u'to forfeit'
	, u'to frame sb.'
	, u'to fraternise'
	, u'to fret (about)'
	, u'to fume (at sb.)'
	, u'to gape'
	, u'to get a dose of the clap'
	, u'to give a leap'
	, u'to give a start'
	, u'to glance'
	, u'to gloat'
	, u'to gnarl'
	, u'to go haywire'
	, u'to go into the matter'
	, u'to grow on sb.'
	, u'to haggle'
	, u'to have a row with sb.'
	, u'to heed'
	, u'to hiss'
	, u'to hoist sb. off'
	, u'to hoodwink'
	, u'to impair'
	, u'to impede'
	, u'to incline'
	, u'to insulate'
	, u'to jeer'
	, u'to jerk'
	, u'to jinx'
	, u'to jostle'
	, u'to know sb. of old'
	, u'to learn sth. (off) by heart'
	, u'to leer'
	, u'to limp'
	, u'to lodge'
	, u'to look harassed'
	, u'to loom up'
	, u'to lumber'
	, u'to lurch'
	, u'to make a beeline for sb./sth.'
	, u'to make a run for it'
	, u'to meddle'
	, u'to mend'
	, u'to mesmerise'
	, u'to moult'
	, u'to nag'
	, u'to neglect'
	, u'to ogle'
	, u'to peck'
	, u'to peer'
	, u'to pelt'
	, u'to perish'
	, u'to pervade'
	, u'to pestle sth.'
	, u'to plummet'
	, u'to pour'
	, u'to precede'
	, u'to preen'
	, u'to prevail'
	, u'to proclaim'
	, u'to prod'
	, u'to protrude'
	, u'to prowl'
	, u'to prune'
	, u'to purse'
	, u'to quail'
	, u'to quiver'
	, u'to recede'
	, u'to reel off sth.'
	, u'to refrain from sth.'
	, u'to rejoice'
	, u'to renounce'
	, u'to replenish'
	, u'to resemble'
	, u'to restrain'
	, u'to retort'
	, u'to rev'
	, u'to reverence'
	, u'to ricochet'
	, u'to rifle through'
	, u'to sack sb.'
	, u'to scarper'
	, u'to scoff'
	, u'to scoop'
	, u'to scorn sth.'
	, u'to scowl'
	, u'to scramble'
	, u'to scurry'
	, u'to scuttle off'
	, u'to see sb. off'
	, u'to seize'
	, u'to shuffle away'
	, u'to shunt'
	, u'to simper'
	, u'to skid'
	, u'to smother'
	, u'to snarl'
	, u'to sneer'
	, u'to snigger'
	, u'to soothe'
	, u'to spiff up'
	, u'to spin sth. off'
	, u'to splutter'
	, u'to sprain'
	, u'to square sb.'
	, u'to squelch'
	, u'to squint'
	, u'to stagger'
	, u'to steady'
	, u'to stride'
	, u'to suffocate'
	, u'to surmise'
	, u'to survey'
	, u'to swagger'
	, u'to swill'
	, u'to swivel'
	, u'to take a leaf out of sbs. book'
	, u'to take sbs. mind off sth.'
	, u'to take the measure of sb.'
	, u'to take the mickey out of sb.'
	, u'to tally'
	, u'to tamper'
	, u'to tarry'
	, u'to tell on sb.'
	, u'to tell sb. off'
	, u'to tether'
	, u'to throng'
	, u'to tingle'
	, u'to tremble'
	, u'to trudge'
	, u'to trundle'
	, u'to twinkle'
	, u'to twitch'
	, u'to usher'
	, u'to ward off'
	, u'to weep'
	, u'to wince'
	, u'to wriggle'
	, u'to writhe'
	, u'to yearn'
	, u'to yield to tempation'
	, u'toad'
	, u'toil'
	, u'tomboy'
	, u'torpor'
	, u'torrent'
	, u'treaty'
	, u'tremulous'
	, u'trench'
	, u'trepidation'
	, u'trespassing'
	, u'tripe'
	, u'trunk'
	, u'turret'
	, u'twinge'
	, u'twitching'
	, u'tyke'
	, u'uncanny'
	, u'unctuous'
	, u'undergrowth'
	, u'undiluted'
	, u'unflinching'
	, u'ungiving'
	, u'unperturbed'
	, u'unscathed'
	, u'velvety'
	, u'verdict'
	, u'vermin'
	, u'veterinarian'
	, u'vicar'
	, u'vindicating'
	, u'vindictiveness'
	, u'vivacious'
	, u'vividly'
	, u'vulture'
	, u'waft'
	, u'ward'
	, u'warlock'
	, u'waspishly'
	, u'wearily'
	, u'weedy'
	, u'well-groomed'
	, u'wheezing'
	, u'whisker'
	, u'whomp'
	, u'whoop'
	, u'wickerwork'
	, u'wig'
	, u'willow'
	, u'wistfully'
	, u'wit'
	, u'withering'
	, u'woe'
	, u'woebegone'
	, u'wolverine'
	, u'wreath'
	, u'wryly'
	, u'yelp'
	, u'abrasive'
	, u'abstaining'
	, u'adamant'
	, u'affiliation'
	, u'ahold'
	, u'aisle'
	, u'akin'
	, u'alumnus'
	, u'amicable'
	, u'aneurysm'
	, u'bankroll'
	, u'blip'
	, u'botched'
	, u'breach'
	, u'budge'
	, u'bumper'
	, u'burr'
	, u'cadence'
	, u'carter'
	, u'caucus'
	, u'chicken-shit'
	, u'chitlins'
	, u'coaster'
	, u'cogent'
	, u'compelling'
	, u'condescending'
	, u'constituents'
	, u'contender'
	, u'contention'
	, u'conure'
	, u'coroner'
	, u'courting'
	, u'cramming'
	, u'cub'
	, u'dago'
	, u'dangling'
	, u'decaf'
	, u'detox'
	, u'diligence'
	, u'dime'
	, u'dipping'
	, u'dissemination'
	, u'dissipated'
	, u'distaste'
	, u'diverted'
	, u'docket'
	, u'duke'
	, u'earmarked'
	, u'edification'
	, u'embroiled'
	, u'eminent'
	, u'evicted'
	, u'filibuster'
	, u'fiscal'
	, u'fixture'
	, u'flattered'
	, u'fling'
	, u'flip-flopping'
	, u'folksy'
	, u'formidable'
	, u'forthcoming'
	, u'forthright'
	, u'frenzy'
	, u'gaffe'
	, u'gauntlet'
	, u'girth'
	, u'gist'
	, u'gravitas'
	, u'gritty'
	, u'gutter'
	, u'hatchback'
	, u'haul'
	, u'hazed'
	, u'holdout'
	, u'hubris'
	, u'impeachment'
	, u'inaugural'
	, u'incendiary'
	, u'incentive'
	, u'incessant'
	, u'inclined'
	, u'indelibly'
	, u'indelicate'
	, u'indentured'
	, u'inebriated'
	, u'intercom'
	, u'interstate'
	, u'invigorating'
	, u'junket'
	, u'knobs'
	, u'lassitude'
	, u'latched'
	, u'lectern'
	, u'ledger'
	, u'leper'
	, u'libertarian'
	, u'livelihood'
	, u'livid'
	, u'loitering'
	, u'luncheon'
	, u'mainline'
	, u'masthead'
	, u'materiel'
	, u'matriculated'
	, u'mumbling'
	, u'municipal'
	, u'municipalities'
	, u'murmuring'
	, u'murmurs'
	, u'nappies'
	, u'negligence'
	, u'negligible'
	, u'op-ed'
	, u'overture'
	, u'pageant'
	, u'pancreas'
	, u'pasture'
	, u'paved'
	, u'pedestal'
	, u'peg'
	, u'persuasion'
	, u'petite'
	, u'pettiness'
	, u'picket'
	, u'planks'
	, u'ploy'
	, u'plumber'
	, u'poaching'
	, u'point-blank'
	, u'precedent'
	, u'preeminence'
	, u'preliminary'
	, u'primaries'
	, u'prob'
	, u'prop'
	, u'pry'
	, u'puff'
	, u'quarrelsome'
	, u'ravished'
	, u'reins'
	, u'relapsed'
	, u'renegade'
	, u'retching'
	, u'retribution'
	, u'rogue'
	, u'rotunda'
	, u'rustling'
	, u'savvy'
	, u'scapegoat'
	, u'schmoozer'
	, u'scolding'
	, u'scout'
	, u'sentinel'
	, u'shackle'
	, u'sham'
	, u'shenanigans'
	, u'shutters'
	, u'slack'
	, u'sledgehammer'
	, u'sludge'
	, u'slugline'
	, u'slurred'
	, u'sobriety'
	, u'solace'
	, u'solicitation'
	, u'solitary'
	, u'sophomore'
	, u'spawned'
	, u'spearheaded'
	, u'sphincter'
	, u'spur-of-the-moment'
	, u'staffer'
	, u'stalemate'
	, u'stammering'
	, u'star-spangled'
	, u'stature'
	, u'stray'
	, u'sublime'
	, u'submission'
	, u'subpoena'
	, u'subsidiaries'
	, u'subsidies'
	, u'supremacy'
	, u'sway'
	, u'swoop'
	, u'tad'
	, u'tame'
	, u'tenants'
	, u'thrush'
	, u'thuds'
	, u'thumping'
	, u'thunderclap'
	, u'to avail'
	, u'to backstab sb.'
	, u'to be bogged'
	, u'to berate'
	, u'to churn'
	, u'to clank'
	, u'to clatter'
	, u'to cobble'
	, u'to convene'
	, u'to cuss'
	, u'to dampen'
	, u'to deplore'
	, u'to devour'
	, u'to dismantle'
	, u'to disrupt'
	, u'to dissuade'
	, u'to dredge'
	, u'to exemplify'
	, u'to exempt'
	, u'to forestall'
	, u'to hump'
	, u'to itemize'
	, u'to kindle'
	, u'to mangle'
	, u'to mimeograph'
	, u'to mull'
	, u'to muster'
	, u'to nosedive'
	, u'to persuade'
	, u'to pitter-patter'
	, u'to ream'
	, u'to refine'
	, u'to reinvigorate'
	, u'to relinquish'
	, u'to schmooze'
	, u'to scoff'
	, u'to screech'
	, u'to solicit'
	, u'to stall'
	, u'to steamroll'
	, u'to stonewall sb.'
	, u'to swerve'
	, u'to tweet'
	, u'to twiddle'
	, u'to unbuckle'
	, u'to vacillate'
	, u'to woo'
	, u'to wrench'
	, u'torpedoing'
	, u'traction'
	, u'trailblazer'
	, u'treading'
	, u'trilateral'
	, u'tutelage'
	, u'twat'
	, u'uncouth'
	, u'uppity'
	, u'valedictorian'
	, u'valiant'
	, u'varsity'
	, u'vassal'
	, u'vetted'
	, u'viable'
	, u'vigilance'
	, u'vindictive'
	, u'vines'
	, u'virtues'
	, u'voracious'
	, u'wacko'
	, u'wantonness'
	, u'watershed'
	, u'wheeler'
	, u'whimpering'
	, u'whirring'
	, u'wholly'
	, u'whooping'
	, u'yadda yadda yadda'
	, u'yapping'
	, u'yelping'
	, u'a whit'
	, u'abhorrent'
	, u'abundance'
	, u'abundantly'
	, u'acquiescence'
	, u'acquisitive'
	, u'acquittal'
	, u'acute'
	, u'adulation'
	, u'advent'
	, u'adversary'
	, u'adverse'
	, u'adversity'
	, u'aegis'
	, u'affluence'
	, u'affluent'
	, u'aggrandizing'
	, u'aggravated'
	, u'ajar'
	, u'alacrity'
	, u'alas'
	, u'allusive'
	, u'altercation'
	, u'amiss'
	, u'ample'
	, u'anguish'
	, u'anxious'
	, u'apostasy'
	, u'appease'
	, u'apposite'
	, u'apprenticeship'
	, u'apt'
	, u'aptitude'
	, u'arcane'
	, u'arson'
	, u'aspirant'
	, u'aspiration'
	, u'assailing'
	, u'asset'
	, u'astute'
	, u'asymptote'
	, u'atrocious'
	, u'attrition'
	, u'auspices'
	, u'auspicious'
	, u'austerity'
	, u'awash'
	, u'awry'
	, u'bait'
	, u'bane'
	, u'banter'
	, u'barista'
	, u'barnacle'
	, u'bawl'
	, u'beats me!'
	, u'beau'
	, u'befuddled'
	, u'belligerence'
	, u'belligerent'
	, u'bereavement'
	, u'betrothal'
	, u'beverage'
	, u'bighead'
	, u'bilious'
	, u'billowing'
	, u'bleak'
	, u'blithely'
	, u'bludgeon'
	, u'bludgeoning'
	, u'bodice'
	, u'booby trap'
	, u'boon'
	, u'bootless'
	, u'borough'
	, u'bosom'
	, u'botch'
	, u'bumpkin'
	, u'bustle'
	, u'by and large'
	, u'calamitous'
	, u'calamity'
	, u'callous'
	, u'candidly'
	, u'candor'
	, u'caprice'
	, u'carcass'
	, u'cavernous'
	, u'cesspool'
	, u'chaff'
	, u'chaste'
	, u'chiefly'
	, u'chime'
	, u'civic'
	, u'clamoring'
	, u'clandestine'
	, u'clemency'
	, u'coercion'
	, u'cohesive'
	, u'commencement'
	, u'commendation'
	, u'compounded'
	, u'compromising'
	, u'compulsive'
	, u'compunction'
	, u'conceit'
	, u'conclusively'
	, u'confines'
	, u'congruent'
	, u'consolation'
	, u'conspicuous'
	, u'consternation'
	, u'constipated'
	, u'constituency'
	, u'constituent'
	, u'contentious'
	, u'contentment'
	, u'contingency'
	, u'contraption'
	, u'conundrum'
	, u'convergence'
	, u'convict'
	, u'conviction'
	, u'convoluted'
	, u'copious'
	, u'corollaries'
	, u'counterfeit'
	, u'covertly'
	, u'cozy'
	, u'credence'
	, u'crimson'
	, u'critters'
	, u'cruical'
	, u'cue'
	, u'customary'
	, u'daft'
	, u'dazzle'
	, u'deadbeat'
	, u'deaf'
	, u'debauched'
	, u'debilitating'
	, u'deceit'
	, u'decent'
	, u'deception'
	, u'decisive'
	, u'decoy'
	, u'decrepit'
	, u'deference'
	, u'deflect'
	, u'defused'
	, u'deigned'
	, u'demise'
	, u'deplorable'
	, u'derelict'
	, u'derision'
	, u'derogatory'
	, u'despairingly'
	, u'desperation'
	, u'despicable'
	, u'deterrent'
	, u'detriment'
	, u'devolution'
	, u'devotion'
	, u'devout'
	, u'dexterous'
	, u'dilapidated'
	, u'diligent'
	, u'disdain'
	, u'dissent'
	, u'distraught'
	, u'distress'
	, u'divulged'
	, u'doggone'
	, u'dormant'
	, u'drab'
	, u'drained'
	, u'drove'
	, u'dust-up'
	, u'eclectic'
	, u'ecstatic'
	, u'effeminate'
	, u'effusive'
	, u'egregious'
	, u'embezzlement'
	, u'enamored'
	, u'entourage'
	, u'entrenched'
	, u'envoy'
	, u'epitome'
	, u'equanimity'
	, u'errant'
	, u'errata'
	, u'esteemed'
	, u'estranged'
	, u'evasive'
	, u'eventually'
	, u'exaltation'
	, u'exalted'
	, u'exemption'
	, u'exhilarating'
	, u'exonerations'
	, u'expedient'
	, u'exultation'
	, u'fair and square'
	, u'fair enough'
	, u'fallacious'
	, u'fallacy'
	, u'farrago'
	, u'febrile'
	, u'fecund'
	, u'fedora'
	, u'feeble'
	, u'felicitously'
	, u'ferocious'
	, u'ferocity'
	, u'ferry'
	, u'fervor'
	, u'fervour'
	, u'fiend'
	, u'flaccid'
	, u'fledgling'
	, u'flurry'
	, u'foible'
	, u'foreknowledge'
	, u'forfeiture'
	, u'forger'
	, u'forlorn'
	, u'fornication'
	, u'fortitude'
	, u'frail'
	, u'fraternity'
	, u'fraudulent'
	, u'fray'
	, u'frivolity'
	, u'frugal'
	, u'frumpy'
	, u'gamut'
	, u'gangrenous'
	, u'garrison'
	, u'ghastly'
	, u'give me a break!'
	, u'gleam'
	, u'glib'
	, u'goon'
	, u'gopher'
	, u'greed'
	, u'grief'
	, u'gristle'
	, u'grit'
	, u'grooming'
	, u'grouse'
	, u'gruff'
	, u'grumble'
	, u'guise'
	, u'hamper'
	, u'hamstrung'
	, u'haughty'
	, u'heresy'
	, u'hicky'
	, u'hindsight'
	, u'hither'
	, u'hoof'
	, u'hothead'
	, u'hue and cry'
	, u'hunch'
	, u'hyperbolic'
	, u'hypocrisy'
	, u'idiosyncratic'
	, u'idolatry'
	, u'if push comes to shove'
	, u'ignominious'
	, u'ilk'
	, u'impartial'
	, u'impending'
	, u'impertinent'
	, u'implacable'
	, u'imposter'
	, u'in lieu [of sth.]'
	, u'inadvertent'
	, u'inane'
	, u'incarcerated'
	, u'inception'
	, u'incessantly'
	, u'incoherent'
	, u'inconceivable'
	, u'incongruously'
	, u'incredulity'
	, u'incursion'
	, u'indelible'
	, u'indignation'
	, u'indulgent'
	, u'ineligible'
	, u'ineptitude'
	, u'inert'
	, u'inextricably'
	, u'infatuated'
	, u'ingenuity'
	, u'iniquity'
	, u'injunction'
	, u'inkling'
	, u'innocuous'
	, u'innuendo'
	, u'insurgency'
	, u'insurgent'
	, u'interlocutor'
	, u'interminable'
	, u'intractable'
	, u'intricate'
	, u'intricately'
	, u'invoice'
	, u'irate'
	, u'itch'
	, u'itinerary'
	, u'jeopardy'
	, u'jibe'
	, u'joint lock'
	, u'judiciary'
	, u'judicious'
	, u'junction'
	, u'juvenile'
	, u'kiln'
	, u'kin'
	, u'kinship'
	, u'knit'
	, u'laddish'
	, u'laudable'
	, u'lauded'
	, u'lavish'
	, u'leaping'
	, u'ledge'
	, u'leeway'
	, u'legerdemain'
	, u'leniency'
	, u'leverage'
	, u'lichens'
	, u'literary'
	, u'litigious'
	, u'loony'
	, u'loot'
	, u'lore'
	, u'lowlife'
	, u'lucidity'
	, u'macronutrient'
	, u'madcap'
	, u'magnanimous'
	, u'magnificent'
	, u'malaise'
	, u'malevolent'
	, u'mason'
	, u'maverick'
	, u'meek'
	, u'mercenary'
	, u'merchant'
	, u'meticulous'
	, u'midget'
	, u'minutiae'
	, u'moniker'
	, u'mother lode'
	, u'muddled'
	, u'myopic'
	, u'myriad'
	, u'napkin'
	, u'nascent'
	, u'natter'
	, u'nauseous'
	, u'nefarious'
	, u'neglected'
	, u'nepotism'
	, u'nescient'
	, u'nonchalance'
	, u'not a/no whit'
	, u'notion'
	, u'notoriety'
	, u'novelty'
	, u'nuisance'
	, u'nutjob'
	, u'oblique'
	, u'oblivion'
	, u'oblivious'
	, u'obnoxious'
	, u'obtrusive'
	, u'odds'
	, u'off one\'s guard'
	, u'omertà'
	, u'on the verge of'
	, u'onslaught'
	, u'onus'
	, u'oomph'
	, u'opinionated'
	, u'opprobrium'
	, u'ostensibly'
	, u'ostentatious'
	, u'ostrich'
	, u'outbound'
	, u'painstaking'
	, u'palatial'
	, u'palpable'
	, u'palsy'
	, u'pariah'
	, u'pastiche'
	, u'pathogen'
	, u'patronage'
	, u'peasant'
	, u'pegged'
	, u'penchant'
	, u'pending'
	, u'penitentiary'
	, u'perilous'
	, u'perseverance'
	, u'persevere'
	, u'pertinent'
	, u'pervasive'
	, u'petulant'
	, u'philandering'
	, u'phony'
	, u'pinnacle'
	, u'pious'
	, u'pithy'
	, u'pittance'
	, u'placid'
	, u'plaintively'
	, u'plank'
	, u'plebiscite'
	, u'pneumatic'
	, u'ponderous'
	, u'populace'
	, u'portent'
	, u'posh'
	, u'posture'
	, u'preaching'
	, u'precedence'
	, u'precept'
	, u'precipice'
	, u'precipitation'
	, u'precipitous'
	, u'precocious'
	, u'predicament'
	, u'predictable'
	, u'predilection'
	, u'predisposed'
	, u'premises'
	, u'preoccupied'
	, u'prepubescent'
	, u'prerequisite'
	, u'prerogative'
	, u'pretense'
	, u'prey'
	, u'prick'
	, u'prig'
	, u'proclivities'
	, u'proficiency'
	, u'profoundly'
	, u'progeny'
	, u'proliferation'
	, u'prolific'
	, u'prone'
	, u'pronouncement'
	, u'propensity'
	, u'propulsion'
	, u'prosaically'
	, u'prosecutor'
	, u'proselytizing'
	, u'prospect'
	, u'prospective'
	, u'protégé'
	, u'provenance'
	, u'prowess'
	, u'pungent'
	, u'purgatory'
	, u'pursuit'
	, u'quaint'
	, u'quarry'
	, u'raft'
	, u'ramification'
	, u'rampant'
	, u'rapacity'
	, u'rapprochement'
	, u'rascal'
	, u'ravage'
	, u'recidivism'
	, u'recital'
	, u'recliner'
	, u'recluse'
	, u'reconciliation'
	, u'rectitude'
	, u'redemtion'
	, u'refinement'
	, u'refutation'
	, u'reimbursement'
	, u'relapse'
	, u'remit'
	, u'replete'
	, u'reproach'
	, u'resilient'
	, u'respite'
	, u'restive'
	, u'restraint'
	, u'resurgent'
	, u'retainer'
	, u'revolting'
	, u'reward'
	, u'ridge'
	, u'rife with'
	, u'right off the bat'
	, u'rigmarole'
	, u'rind'
	, u'rote'
	, u'runt'
	, u'ruse'
	, u'ruthless'
	, u'salacious'
	, u'sanguinary'
	, u'sanguine'
	, u'sapling'
	, u'savage'
	, u'savior'
	, u'scavenging'
	, u'schism'
	, u'scintillating'
	, u'scoundrel'
	, u'scourge'
	, u'scrutiny'
	, u'sedulous'
	, u'seep'
	, u'self-indulgence'
	, u'seminal'
	, u'senescence'
	, u'sensible'
	, u'sentient'
	, u'serendipity'
	, u'serene'
	, u'serfdom'
	, u'sermon'
	, u'shaggy'
	, u'shard'
	, u'shrill'
	, u'shriveled'
	, u'shunning'
	, u'signet'
	, u'simmer'
	, u'simulacrum'
	, u'skank'
	, u'skirmish'
	, u'slander'
	, u'snafu'
	, u'sobriquet'
	, u'solicitor'
	, u'solstice'
	, u'soothsayer'
	, u'soubriquet'
	, u'sparring'
	, u'specimen'
	, u'specious'
	, u'speciously'
	, u'spool'
	, u'spot-on'
	, u'squalid'
	, u'squall'
	, u'squatters'
	, u'squeamish'
	, u'stake'
	, u'starry'
	, u'stead'
	, u'stipend'
	, u'stirrup'
	, u'stoop'
	, u'stratification'
	, u'streamline'
	, u'strident'
	, u'strife'
	, u'strop'
	, u'stubble'
	, u'subservient'
	, u'succinct'
	, u'suffrage'
	, u'sulking'
	, u'sultry'
	, u'summit'
	, u'summitry'
	, u'sumptuous'
	, u'superciliousness'
	, u'superfluous'
	, u'susceptibility'
	, u'susceptible'
	, u'sustenance'
	, u'swathe'
	, u'sweet spot'
	, u'swift'
	, u'tacitly'
	, u'tangible'
	, u'tanner'
	, u'tantamount'
	, u'tawdry'
	, u'temerity'
	, u'tenacious'
	, u'tenacity'
	, u'tenuous'
	, u'terse'
	, u'thrall'
	, u'thrifty'
	, u'throttle'
	, u'ticks'
	, u'timidity'
	, u'tinker'
	, u'titillating'
	, u'to abide'
	, u'to accost'
	, u'to alleviate'
	, u'to allude'
	, u'to allure'
	, u'to amount to sth.'
	, u'to amplify'
	, u'to annex'
	, u'to anticipate'
	, u'to apprehend'
	, u'to approach'
	, u'to assert'
	, u'to assess'
	, u'to assuage'
	, u'to attune'
	, u'to bargain'
	, u'to be adept in sth.'
	, u'to be complicit in sth.'
	, u'to be considered fair game'
	, u'to be gobsmacked'
	, u'to be hard pressed'
	, u'to be in one\'s prime'
	, u'to be in thrall to sb./sth.'
	, u'to be indepted'
	, u'to be obliged'
	, u'to be skint'
	, u'to be/go awol'
	, u'to behold'
	, u'to behoove'
	, u'to belittle'
	, u'to bestow upon'
	, u'to bolster'
	, u'to botch sth. up'
	, u'to buck sth.'
	, u'to buckle up'
	, u'to buoy up'
	, u'to burgeon'
	, u'to canvas'
	, u'to cede'
	, u'to cherish'
	, u'to churn out'
	, u'to circumvent'
	, u'to clam up'
	, u'to cling to'
	, u'to coalesce'
	, u'to coddle'
	, u'to coerce'
	, u'to coincide'
	, u'to compel'
	, u'to comprehend'
	, u'to comprise'
	, u'to concede'
	, u'to conclude'
	, u'to condone'
	, u'to confer'
	, u'to confess'
	, u'to conflate'
	, u'to content'
	, u'to converge'
	, u'to corroborate'
	, u'to countenance'
	, u'to craft'
	, u'to cram'
	, u'to cut corners'
	, u'to debauch'
	, u'to deduce'
	, u'to denigrate'
	, u'to denote'
	, u'to depict'
	, u'to deplete'
	, u'to deride'
	, u'to despair'
	, u'to deter'
	, u'to devise'
	, u'to devolve'
	, u'to diffuse'
	, u'to dignify'
	, u'to digress'
	, u'to dismay sb.'
	, u'to disparage'
	, u'to dodge'
	, u'to double-cross sb.'
	, u'to drain'
	, u'to dupe'
	, u'to dwell'
	, u'to dwell upon'
	, u'to elucidate'
	, u'to emanate'
	, u'to embark on sth.'
	, u'to empower'
	, u'to encompass'
	, u'to endorse'
	, u'to endow'
	, u'to engross'
	, u'to engulf'
	, u'to entice'
	, u'to entrench'
	, u'to epitomize'
	, u'to eschew'
	, u'to exacerbate'
	, u'to exasperate'
	, u'to excoriate'
	, u'to exert'
	, u'to exonerate'
	, u'to explicate'
	, u'to extol'
	, u'to exude'
	, u'to facilitate'
	, u'to fare'
	, u'to flail'
	, u'to flatter sb.'
	, u'to floor'
	, u'to foil'
	, u'to forsake'
	, u'to fortify'
	, u'to furnish'
	, u'to gallow'
	, u'to gentrify'
	, u'to get riled up'
	, u'to get shafted'
	, u'to go out of one\'s way'
	, u'to go sideways'
	, u'to haul off'
	, u'to have one\'s mind in the gutter'
	, u'to head for/to splitsville'
	, u'to hedge'
	, u'to humble'
	, u'to imbue'
	, u'to imperil'
	, u'to implicate'
	, u'to impugn sth.'
	, u'to induce'
	, u'to indulge'
	, u'to ingrain'
	, u'to inoculate'
	, u'to instigate'
	, u'to instill'
	, u'to intimidate'
	, u'to intuit'
	, u'to invigorate'
	, u'to jab'
	, u'to jury-rig'
	, u'to languish'
	, u'to lie low'
	, u'to linger'
	, u'to loom'
	, u'to maim'
	, u'to merit'
	, u'to mold'
	, u'to nab'
	, u'to oblige'
	, u'to obliterate'
	, u'to occasion'
	, u'to ostracize'
	, u'to outdo sb.'
	, u'to outfit'
	, u'to pass down'
	, u'to patronize sb.'
	, u'to perceive sth.'
	, u'to permeate'
	, u'to perpetrate'
	, u'to persist'
	, u'to perturb'
	, u'to peruse'
	, u'to pontificate'
	, u'to preclude'
	, u'to preordain'
	, u'to propound'
	, u'to pule'
	, u'to purport'
	, u'to rack up'
	, u'to ratchet up'
	, u'to reap'
	, u'to reel'
	, u'to regurgitate'
	, u'to reify'
	, u'to repudiate'
	, u'to rescind'
	, u'to resuscitate'
	, u'to retreat'
	, u'to reverberate'
	, u'to revere'
	, u'to revile'
	, u'to roil'
	, u'to scold'
	, u'to scour'
	, u'to scrutinise'
	, u'to secede'
	, u'to shush'
	, u'to sneak up to'
	, u'to sober up'
	, u'to spare'
	, u'to sprawl'
	, u'to spur'
	, u'to squander'
	, u'to stand sb. up'
	, u'to stash'
	, u'to stoke'
	, u'to strive'
	, u'to tee'
	, u'to thrive'
	, u'to thwart'
	, u'to tower'
	, u'to transpire'
	, u'to upend'
	, u'to vanquish'
	, u'to veer'
	, u'to vindicate'
	, u'to wither away'
	, u'to yank'
	, u'topple'
	, u'tractable'
	, u'travail'
	, u'trollop'
	, u'trundle'
	, u'tureen'
	, u'unabridged'
	, u'unapproachable'
	, u'unbecoming'
	, u'unbridled'
	, u'untenable'
	, u'unwind'
	, u'valetudinarian'
	, u'vastness'
	, u'vaudevillian'
	, u'vaunted'
	, u'vehemence'
	, u'venal'
	, u'veneer'
	, u'veneration'
	, u'veracity'
	, u'vestige'
	, u'vexation'
	, u'viability'
	, u'vicissitude'
	, u'virility'
	, u'visitation'
	, u'vivified'
	, u'vocational'
	, u'volition'
	, u'vouchsafing'
	, u'wag'
	, u'waiver'
	, u'warped'
	, u'wedlock'
	, u'welter'
	, u'whiff'
	, u'wily'
	, u'wimp'
	, u'wisecrack'
	, u'witticism'
	, u'zany'
	, u'zealot'
]))
