-- EK_C_0.3 - Lua referencia-implementáció
--
-- Cél:
--   Category -> Topic -> Pointer
--   write-back cache
--   policy ellenőrzés
--   relációk
--   conflict resolver
--   SYSERR log
--
-- Ez egy Lua 5.4 referencia-változat.
-- SQLite/perzisztencia nélkül, standard Lua-val is futtatható.
-- A tényleges DB-adapter külön rétegként cserélhető be.

local EK = {
    version = "C_0.3",
    status = "MINIMAL_REFERENCE",
    valid_relations = {
        Related = true,
        Parent = true,
        Child = true,
        DependsOn = true,
        Source = true,
        Similar = true
    }
}

local function now()
    return os.date("!%Y-%m-%dT%H:%M:%SZ")
end

local function syserr(component, message)
    local f = io.open("ek_syserr.log", "a")
    if f then
        f:write(string.format(
            "SYSERR: %s :: %s: %s\n",
            now(), component, message
        ))
        f:close()
    end
end

local function contains(text, needle)
    return string.find(
        string.lower(text),
        string.lower(needle),
        1,
        true
    ) ~= nil
end

-- A policy külön fájlban tartható.
-- Egyszerű Lua formátumú policy példa:
EK.policy = {
    blocked_terms = {
        -- A tényleges lista projekt-specifikusan töltendő be.
    }
}

function EK.precheck(text)
    local hits = {}

    for _, term in ipairs(EK.policy.blocked_terms) do
        if contains(text, term) then
            table.insert(hits, term)
        end
    end

    if #hits > 0 then
        syserr("POLICY", "query blocked")
        return false, hits
    end

    return true, hits
end

EK.store = {
    pointers = {},
    relations = {},
    next_id = 1
}

EK.cache = {
    pending = {},
    flush_every = 10
}

function EK.add_pointer(category, topic, source, summary, last_checked, confidence)
    if not category or not topic or not source or not summary then
        error("category/topic/source/summary kötelező")
    end

    if confidence ~= nil and (confidence < 0 or confidence > 100) then
        error("confidence 0..100 között lehet")
    end

    local pointer = {
        id = EK.store.next_id,
        category = category,
        topic = topic,
        source = source,
        summary = summary,
        last_checked = last_checked,
        confidence = confidence
    }

    EK.store.next_id = EK.store.next_id + 1
    table.insert(EK.cache.pending, pointer)

    if #EK.cache.pending >= EK.cache.flush_every then
        EK.flush()
    end

    return pointer.id
end

function EK.flush()
    for _, pointer in ipairs(EK.cache.pending) do
        table.insert(EK.store.pointers, pointer)
    end

    EK.cache.pending = {}
end

local function searchable(pointer)
    return table.concat({
        pointer.category or "",
        pointer.topic or "",
        pointer.summary or ""
    }, " ")
end

function EK.search(query, limit)
    limit = limit or 10

    local allowed, hits = EK.precheck(query)
    if not allowed then
        return {}, {
            status = "BLOCKED",
            hits = hits
        }
    end

    local results = {}

    for _, pointer in ipairs(EK.store.pointers) do
        local score = 0

        for token in string.gmatch(
            string.lower(query),
            "%S+"
        ) do
            if #token >= 2 and contains(searchable(pointer), token) then
                score = score + 1
            end
        end

        if score > 0 then
            table.insert(results, {
                pointer = pointer,
                score = score
            })
        end
    end

    table.sort(results, function(a, b)
        if a.score ~= b.score then
            return a.score > b.score
        end

        local ac = a.pointer.confidence or -1
        local bc = b.pointer.confidence or -1

        return ac > bc
    end)

    local output = {}
    for i = 1, math.min(limit, #results) do
        table.insert(output, results[i].pointer)
    end

    return output, {
        status = #output > 0 and "OK" or "NO_RESULT"
    }
end

function EK.add_relation(source_id, target_id, relation)
    if not EK.valid_relations[relation] then
        syserr("RELATION", "invalid relation: " .. tostring(relation))
        return false, "INVALID_RELATION"
    end

    table.insert(EK.store.relations, {
        source_id = source_id,
        target_id = target_id,
        relation = relation
    })

    return true
end

function EK.get_relations(pointer_id)
    local result = {}

    for _, relation in ipairs(EK.store.relations) do
        if relation.source_id == pointer_id then
            table.insert(result, relation)
        end
    end

    return result
end

function EK.resolve_conflict(pointers)
    if #pointers == 0 then
        return {
            status = "NO_RESULT",
            message = "Nincs releváns EK pointer.",
            recommendation = nil
        }
    end

    local ranked = {}
    for _, pointer in ipairs(pointers) do
        table.insert(ranked, pointer)
    end

    table.sort(ranked, function(a, b)
        local ac = a.confidence or -1
        local bc = b.confidence or -1
        return ac > bc
    end)

    local ranked_ids = {}
    for _, pointer in ipairs(ranked) do
        table.insert(ranked_ids, pointer.id)
    end

    return {
        status = "REVIEW_REQUIRED",
        message = "A találatok rangsorolva vannak; végső választás nem történik automatikusan.",
        recommendation = ranked[1].id,
        ranked_ids = ranked_ids
    }
end

-- Egyszerű demo
local function demo()
    local a = EK.add_pointer(
        "Tudomány_Űr",
        "Nap_és_égés",
        "https://science.nasa.gov/sun",
        "A Nap energiatermelése nukleáris fúzióhoz kapcsolódik.",
        "2026-03-17",
        98
    )

    local b = EK.add_pointer(
        "Technológia_AI",
        "EK_rendszer",
        "internal_EK_system",
        "Hierarchikus pointer-alapú külső memória.",
        "2026-08-08",
        100
    )

    EK.flush()

    EK.add_relation(b, a, "Related")

    local results, meta = EK.search("EK pointer külső memória")

    print("Search status: " .. meta.status)

    for _, pointer in ipairs(results) do
        print(string.format(
            "[%d] %s/%s -> %s",
            pointer.id,
            pointer.category,
            pointer.topic,
            pointer.source
        ))
    end

    local decision = EK.resolve_conflict(results)

    print("Conflict status: " .. decision.status)
    print("Recommendation: " .. tostring(decision.recommendation))
end

demo()

return EK
