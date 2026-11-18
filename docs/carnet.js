(() => {
  const storageKey = 'bible-strong-carnet-v1';
  const own = (object, key) => Object.hasOwn(object, key);
  const validRef = ref => /^[A-Za-z0-9]+\.[1-9]\d{0,2}\.[1-9]\d{0,2}$/.test(ref);
  const suggested = ['Prière', 'Foi', 'À étudier'];
  const colors = {yellow: 'Jaune', green: 'Vert', blue: 'Bleu', pink: 'Rose', purple: 'Violet'};
  const fresh = () => ({version: 1, categories: [], verses: {}});
  function validate(value) {
    if (value?.version !== 1 || !Array.isArray(value.categories) ||
        !value.verses || typeof value.verses !== 'object' || Array.isArray(value.verses)) {
      throw Error('Ce fichier n’est pas une sauvegarde Bible Strong compatible.');
    }
    const categories = [...new Set(value.categories.map(name => {
      if (typeof name !== 'string' || !name.trim() || name.length > 80) throw Error('Catégorie invalide.');
      return name.trim();
    }))];
    const verses = {};
    for (const [ref, item] of Object.entries(value.verses)) {
      if (!validRef(ref) || !Array.isArray(item?.categories) ||
          !item.categories.every(name => categories.includes(name)) ||
          typeof item.note !== 'string') throw Error('Verset ou note invalide.');
      verses[ref] = {categories: [...new Set(item.categories)], note: item.note};
      if (item.color !== undefined) {
        if (item.color !== null && (typeof item.color !== 'string' || !own(colors, item.color))) {
          throw Error('Couleur de surlignage invalide.');
        }
        verses[ref].color = item.color;
      }
    }
    return {version: 1, categories, verses};
  }
  const load = () => {
    const raw = localStorage.getItem(storageKey);
    return raw ? validate(JSON.parse(raw)) : fresh();
  };
  const clone = value => JSON.parse(JSON.stringify(value));
  const element = (tag, value) => {
    const node = document.createElement(tag);
    if (value !== undefined) node.textContent = value;
    return node;
  };
  const button = (label, action) => {
    const node = element('button', label);
    node.type = 'button';
    node.addEventListener('click', action);
    return node;
  };
  const dialog = element('dialog');
  dialog.className = 'carnet';
  dialog.setAttribute('aria-labelledby', 'carnet-title');
  document.body.append(dialog);
  const status = element('p');
  status.setAttribute('role', 'status');
  function frame(title) {
    const heading = element('h2', title);
    heading.id = 'carnet-title';
    status.textContent = '';
    dialog.replaceChildren(heading, button('Fermer', () => dialog.close()), status);
    if (!dialog.open) dialog.showModal();
  }
  function report(error) {
    status.textContent = error.message || 'Impossible d’accéder au carnet sur cet appareil.';
  }
  const update = change => {
    const state = load();
    change(state);
    localStorage.setItem(storageKey, JSON.stringify(validate(state)));
    paintHighlights(state);
  };
  function edit(ref) {
    frame(refName(ref));
    try {
      const state = load();
      const selected = new Set(state.verses[ref]?.categories || []);
      const categories = element('fieldset');
      categories.append(element('legend', 'Enregistrer dans les catégories'));
      const addChoice = name => {
        const label = element('label');
        const checkbox = element('input');
        checkbox.type = 'checkbox';
        checkbox.checked = selected.has(name);
        checkbox.onchange = () => checkbox.checked ? selected.add(name) : selected.delete(name);
        label.append(checkbox, document.createTextNode(' ' + name));
        categories.append(label);
        return checkbox;
      };
      const choices = new Map([...new Set([...suggested, ...state.categories])].map(name => [name, addChoice(name)]));
      const name = element('input');
      name.maxLength = 80;
      name.placeholder = 'Nouvelle catégorie';
      name.setAttribute('aria-label', 'Nouvelle catégorie');
      const add = () => {
        const value = name.value.trim();
        if (!value) return;
        if (!choices.has(value)) choices.set(value, addChoice(value));
        choices.get(value).checked = true;
        selected.add(value);
        name.value = '';
      };
      const noteLabel = element('label', 'Note personnelle');
      const note = element('textarea');
      note.rows = 5;
      note.value = state.verses[ref]?.note || '';
      noteLabel.append(note);
      const colorLabel = element('fieldset');
      colorLabel.className = 'highlight-palette';
      colorLabel.append(element('legend', 'Surlignage'));
      let selectedColor = state.verses[ref]?.color || '';
      for (const [value, label] of [['', 'Aucun'], ...Object.entries(colors)]) {
        const choice = element('label');
        if (value) choice.dataset.highlight = value;
        const option = element('input');
        option.type = 'radio';
        option.name = 'highlight-color';
        option.value = value;
        option.checked = selectedColor === value;
        option.onchange = () => { selectedColor = value; };
        choice.append(option, document.createTextNode(label));
        colorLabel.append(choice);
      }
      dialog.append(colorLabel, categories, name, button('Ajouter la catégorie', add), noteLabel,
        button('Enregistrer', () => {
          try {
            add();
            update(current => {
              current.categories = [...new Set([...current.categories, ...selected])];
              if (selected.size || note.value.trim() || selectedColor) {
                current.verses[ref] = {categories: [...selected], note: note.value.trim(), color: selectedColor || null};
              } else {
                delete current.verses[ref];
              }
            });
            dialog.close();
            notify('Verset mis à jour.');
          } catch (error) { report(error); }
        }));
    } catch (error) { report(error); }
  }
  function merge(current, incoming) {
    current.categories = [...new Set([...current.categories, ...incoming.categories])];
    for (const [ref, item] of Object.entries(incoming.verses)) {
      if (!own(current.verses, ref)) {
        current.verses[ref] = clone(item);
        continue;
      }
      const existing = current.verses[ref];
      existing.categories = [...new Set([...existing.categories, ...item.categories])];
      if (own(item, 'color')) existing.color = item.color;
      const separator = '\n\n— Note importée —\n';
      if (item.note && !existing.note.split(separator).includes(item.note)) {
        existing.note = [existing.note, item.note].filter(Boolean).join(separator);
      }
    }
  }
  function show() {
    frame('Mes versets');
    try {
      const state = load();
      const exportButton = button('Exporter', () => {
        try {
          const url = URL.createObjectURL(new Blob([JSON.stringify(load(), null, 2)], {type: 'application/json'}));
          const link = element('a');
          link.href = url;
          link.download = 'bible-strong-mes-versets.json';
          document.body.append(link);
          link.click();
          link.remove();
          setTimeout(() => URL.revokeObjectURL(url), 30000);
        } catch (error) { report(error); }
      });
      const file = element('input');
      file.type = 'file';
      file.accept = '.json,application/json';
      file.hidden = true;
      file.onchange = async () => {
        try {
          if (!file.files[0]) return;
          const incoming = validate(JSON.parse(await file.files[0].text()));
          for (const ref of Object.keys(incoming.verses)) {
            const [id, chapter, verse] = ref.split('.');
            const bookInfo = books.find(book => book.id === id);
            if (!bookInfo || +chapter > bookInfo.chapters || +verse > 176) throw Error('Référence inconnue dans la sauvegarde.');
          }
          update(current => merge(current, incoming));
          show();
          status.textContent = 'Sauvegarde importée.';
        } catch (error) { report(error); }
        finally { file.value = ''; }
      };
      dialog.append(exportButton, button('Importer', () => file.click()), file);
      const entries = Object.entries(state.verses);
      if (!entries.length) dialog.append(element('p', 'Touchez le numéro d’un verset pour l’enregistrer.'));
      const groups = [...state.categories.map(name => [name, entries.filter(([, item]) => item.categories.includes(name))]),
        ['Sans catégorie', entries.filter(([, item]) => !item.categories.length)]];
      for (const [name, items] of groups) {
        if (!items.length) continue;
        const group = element('details');
        group.append(element('summary', name + ' (' + items.length + ')'));
        for (const [ref, item] of items) {
          const row = element('div');
          if (item.color) row.dataset.highlight = item.color;
          row.append(button(refName(ref), () => { dialog.close(); navigateRef(ref); }),
            button('Modifier', () => edit(ref)));
          if (item.note) {
            const note = element('p', item.note);
            note.className = 'carnet-note';
            row.append(note);
          }
          group.append(row);
        }
        dialog.append(group);
      }
    } catch (error) { report(error); }
  }
  const launcher = button('Mes versets', show);
  document.querySelector('.readingbar > div').prepend(launcher);
  const verses = document.querySelector('#verses');
  function paintHighlights(state) {
    for (const trigger of verses.querySelectorAll('.carnet-trigger')) {
      const verse = trigger.closest('.verse');
      const color = state.verses[trigger.dataset.carnetRef]?.color;
      if (color) verse.dataset.highlight = color;
      else delete verse.dataset.highlight;
    }
  }
  function enableVerseMenus() {
    for (const number of verses.querySelectorAll('span.verse-number')) {
      const ref = [book, chapter, number.textContent].join('.');
      const trigger = button(number.textContent, () => edit(ref));
      trigger.className = 'verse-number carnet-trigger';
      trigger.dataset.carnetRef = ref;
      trigger.setAttribute('aria-label', 'Surligner, enregistrer ou annoter ' + refName(ref));
      number.replaceWith(trigger);
    }
    try { paintHighlights(load()); } catch { /* Le menu affiche les erreurs du carnet. */ }
  }
  new MutationObserver(enableVerseMenus).observe(verses, {childList: true});
  enableVerseMenus();
})();
